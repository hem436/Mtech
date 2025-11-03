#!/usr/bin/env python3
"""
Streamlit Application for Next Word Prediction using MLP Language Models.

This app allows users to:
1. Select trained model variants (different embedding dims, activations, etc.)
2. Input text and predict the next k words
3. Control prediction randomness via temperature
4. Handle out-of-vocabulary (OOV) words with multiple strategies
5. Visualize prediction results

Features:
- Two model categories: Unstructured text (essays, literature) and Structured text (code)
- Multiple OOV handling strategies: Skip, Use most similar word, Use <UNK> token
- Temperature-based sampling for controlled randomness
- Real-time model predictions with context window adjustment
"""

import os
import sys
import random
import re
from collections import defaultdict
from typing import List, Dict, Tuple, Optional
import warnings

import numpy as np
import torch
import torch.nn.functional as F
from torch import nn
import streamlit as st
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.manifold import TSNE
import plotly.graph_objects as go

# =============================================================================
# MODEL ARCHITECTURE
# =============================================================================

class MLPTextGenerator(nn.Module):
    """
    MLP-based text generation model that predicts the next word given a context.
    
    Architecture:
    - Embedding layer converts word indices to embeddings
    - Multiple hidden layers with optional activation functions
    - Output layer produces logits over the vocabulary
    """
    
    def __init__(self, vocab_size, embedding_dim, context_length, hidden_dims, activation_fn):
        super().__init__()
        self.embedding = nn.Embedding(vocab_size, embedding_dim)
        layers = []
        input_dim = embedding_dim * context_length
        for hidden_dim in hidden_dims:
            layers.append(nn.Linear(input_dim, hidden_dim))
            if activation_fn == 'relu':
                layers.append(nn.ReLU())
            elif activation_fn == 'tanh':
                layers.append(nn.Tanh())
            input_dim = hidden_dim
        layers.append(nn.Linear(input_dim, vocab_size))
        self.mlp = nn.Sequential(*layers)
    
    def forward(self, x):
        emb = self.embedding(x)
        emb = emb.view(emb.size(0), -1)
        logits = self.mlp(emb)
        return F.log_softmax(logits, dim=-1)
    
    def get_embedding_layer(self):
        """Returns the embedding layer for similarity computations."""
        return self.embedding


# =============================================================================
# VOCABULARY AND OOV HANDLING
# =============================================================================

class VocabularyManager:
    """
    Manages vocabulary, word-to-index mappings, and out-of-vocabulary word handling.
    """
    
    def __init__(self, stoi: Dict, itos: Dict, embeddings: Optional[torch.Tensor] = None):
        """
        Args:
            stoi: String-to-index mapping dictionary
            itos: Index-to-string mapping dictionary
            embeddings: Embedding matrix for similarity-based OOV handling
        """
        self.stoi = stoi
        self.itos = itos
        self.embeddings = embeddings
        self.vocab_size = len(stoi)
        
        # Precompute special token indices
        self.pad_idx = stoi.get('<PAD>', 0)
        self.unk_idx = stoi.get('<UNK>', None)
    
    def is_oov(self, word: str) -> bool:
        """Check if a word is out-of-vocabulary."""
        return word not in self.stoi
    
    def get_index(self, word: str, strategy: str = 'skip') -> Optional[int]:
        """
        Get the index for a word, handling OOV cases.
        
        Strategies:
        - 'skip': Skip OOV words entirely
        - 'unk': Use <UNK> token if available
        - 'similar': Find most similar word in vocabulary using embeddings
        
        Args:
            word: The word to get index for
            strategy: OOV handling strategy
        
        Returns:
            Word index or None if should be skipped
        """
        if word in self.stoi:
            return self.stoi[word]
        
        if strategy == 'skip':
            return None
        elif strategy == 'unk':
            if self.unk_idx is not None:
                return self.unk_idx
            # Fallback to most frequent word if <UNK> not available
            return self.stoi.get('<PAD>', 0)
        elif strategy == 'similar':
            return self._find_similar_word(word)
        else:
            return None
    
    def _find_similar_word(self, word: str) -> int:
        """
        Find the most similar word in vocabulary using embedding similarity.
        Uses character-level similarity as a fast approximation.
        
        Args:
            word: The OOV word
        
        Returns:
            Index of most similar word in vocabulary
        """
        if not self.embeddings is None:
            try:
                # Use character n-gram similarity as a quick heuristic
                best_match = None
                best_score = -1
                
                for vocab_word in self.stoi.keys():
                    if vocab_word.startswith('<'):  # Skip special tokens
                        continue
                    
                    # Simple character overlap score
                    common = sum(1 for c in word if c in vocab_word)
                    score = 2 * common / (len(word) + len(vocab_word))
                    
                    if score > best_score:
                        best_score = score
                        best_match = self.stoi[vocab_word]
                
                return best_match if best_match is not None else self.stoi.get('<PAD>', 0)
            except Exception:
                pass
        
        # Fallback: return <PAD> token
        return self.stoi.get('<PAD>', 0)
    
    def words_to_indices(self, words: List[str], strategy: str = 'skip') -> List[int]:
        """
        Convert a list of words to indices, handling OOV words.
        
        Args:
            words: List of words
            strategy: OOV handling strategy
        
        Returns:
            List of word indices (may be shorter if using 'skip' strategy)
        """
        indices = []
        for word in words:
            idx = self.get_index(word, strategy)
            if idx is not None:
                indices.append(idx)
        return indices
    
    def indices_to_words(self, indices: List[int]) -> List[str]:
        """Convert a list of indices to words."""
        return [self.itos.get(idx, '<UNK>') for idx in indices]


# =============================================================================
# PREDICTION ENGINE
# =============================================================================

class TextPredictionEngine:
    """
    Engine for generating next word predictions with temperature-based sampling.
    """
    
    def __init__(self, model, vocab_manager: VocabularyManager, context_length: int, device='cpu'):
        """
        Args:
            model: Trained MLPTextGenerator model
            vocab_manager: VocabularyManager instance
            context_length: Length of context window
            device: 'cpu' or 'cuda'
        """
        self.model = model.to(device)
        self.model.eval()
        self.vocab_manager = vocab_manager
        self.context_length = context_length
        self.device = device
    
    def predict_next_words(
        self,
        context_words: List[str],
        num_words: int = 5,
        temperature: float = 1.0,
        oov_strategy: str = 'skip',
        seed: Optional[int] = None
    ) -> List[str]:
        """
        Predict the next words given a context.
        
        Args:
            context_words: List of context words
            num_words: Number of words to predict
            temperature: Sampling temperature (>1 more random, <1 more deterministic)
            oov_strategy: How to handle out-of-vocabulary words
            seed: Random seed for reproducibility
        
        Returns:
            List of predicted words
        """
        if seed is not None:
            torch.manual_seed(seed)
            np.random.seed(seed)
            random.seed(seed)
        
        # Convert context words to indices
        context_indices = self.vocab_manager.words_to_indices(context_words, oov_strategy)
        
        # Pad context to required length
        if len(context_indices) < self.context_length:
            context = [self.vocab_manager.pad_idx] * (self.context_length - len(context_indices)) + context_indices
        else:
            context = context_indices[-self.context_length:]
        
        predictions = []
        
        with torch.no_grad():
            for _ in range(num_words):
                # Convert context to tensor
                context_tensor = torch.tensor([context], dtype=torch.long).to(self.device)
                
                # Get model output (log probabilities)
                log_probs = self.model(context_tensor)
                
                # Apply temperature scaling
                if temperature != 1.0:
                    # Convert log probabilities to probabilities, apply temperature, convert back
                    probs = torch.exp(log_probs) ** (1.0 / temperature)
                    probs = probs / probs.sum(dim=-1, keepdim=True)
                    predicted_idx = torch.multinomial(probs[0], 1).item()
                else:
                    # Greedy selection (most likely word)
                    predicted_idx = log_probs.argmax(dim=1).item()
                
                predicted_word = self.vocab_manager.itos.get(predicted_idx, '<UNK>')
                predictions.append(predicted_word)
                
                # Update context for next iteration
                context = context[1:] + [predicted_idx]
        
        return predictions
    
    def predict_with_confidence(
        self,
        context_words: List[str],
        num_words: int = 5,
        temperature: float = 1.0,
        oov_strategy: str = 'skip',
        seed: Optional[int] = None,
        top_k: int = 5
    ) -> List[Tuple[str, float]]:
        """
        Predict next words with confidence scores.
        
        Args:
            context_words: List of context words
            num_words: Number of words to predict
            temperature: Sampling temperature
            oov_strategy: How to handle out-of-vocabulary words
            seed: Random seed
            top_k: Return top-k alternative predictions
        
        Returns:
            List of (word, confidence) tuples for each prediction position
        """
        if seed is not None:
            torch.manual_seed(seed)
            np.random.seed(seed)
            random.seed(seed)
        
        # Convert context words to indices
        context_indices = self.vocab_manager.words_to_indices(context_words, oov_strategy)
        
        # Pad context
        if len(context_indices) < self.context_length:
            context = [self.vocab_manager.pad_idx] * (self.context_length - len(context_indices)) + context_indices
        else:
            context = context_indices[-self.context_length:]
        
        predictions_with_confidence = []
        
        with torch.no_grad():
            for _ in range(num_words):
                context_tensor = torch.tensor([context], dtype=torch.long).to(self.device)
                log_probs = self.model(context_tensor)
                
                # Get top-k predictions
                top_log_probs, top_indices = torch.topk(log_probs[0], min(top_k, len(self.vocab_manager.stoi)))
                
                # Convert log probabilities to probabilities
                top_probs = torch.exp(top_log_probs).cpu().numpy()
                
                # Greedy prediction (highest probability)
                predicted_idx = top_indices[0].item()
                predicted_word = self.vocab_manager.itos.get(predicted_idx, '<UNK>')
                confidence = float(top_probs[0])
                
                predictions_with_confidence.append((predicted_word, confidence))
                
                # Update context
                context = context[1:] + [predicted_idx]
        
        return predictions_with_confidence


# =============================================================================
# MODEL LOADING AND MANAGEMENT
# =============================================================================

@st.cache_resource
def load_model_config() -> Dict:
    """Load and return model configuration."""
    return {
        'context_length': 5,
        'embedding_dims': [32, 64],
        'hidden_layer_configs': [[1024], [1024, 1024]],
        'activations': ['relu', 'tanh'],
    }


def create_context_target_pairs(file_path, context_length, stoi, max_words=None):
    """
    Create context-target pairs from a file (same as in notebook).
    
    Args:
        file_path (str): Path to the text file
        context_length (int): Number of words in context
        stoi (dict): String-to-index mapping
        max_words (int, optional): Maximum words to process
    
    Yields:
        tuple: (context_idx, target_idx)
    """
    words_processed = 0
    stoi['<PAD>'] = 0
    context = [stoi['<PAD>']] * context_length
    
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            for line in f:
                words = line.strip().split()
                if len(words) <= context_length:
                    continue
                if max_words is not None and words_processed >= max_words:
                    break
                for word in words:
                    if max_words is not None and words_processed >= max_words:
                        break
                    if word == '<start>':
                        context = [stoi['<PAD>']] * context_length
                        continue
                    if word not in stoi:
                        stoi[word] = len(stoi)
                    target = stoi[word]
                    yield (context, target)
                    context = context[1:] + [stoi[word]]
                    words_processed += 1
    except FileNotFoundError:
        pass


@st.cache_resource
def load_vocab(category: str) -> Tuple[Dict, Dict]:
    """
    Build vocabulary by processing subset files (same as notebook approach).
    This ensures the vocabulary size matches the trained models exactly.
    
    Args:
        category: 'structured' or 'unstructured'
    
    Returns:
        Tuple of (stoi, itos) dictionaries
    """
    base_path = './struct_model' if category == 'structured' else './unstruct_model'
    
    # Determine which datasets to use based on category
    datasets_info = [
        ('Stacks', False),
        ('Linux Code', False),
    ] if category == 'structured' else [
         ('Wikipedia', True),
        ('Paul Graham Essays', True),
        ('War and Peace', True),
        ('Sherlock', True),
    ]
    
    # Build vocabulary by processing subset files (creates correct size)
    # This matches the notebook's approach exactly
    stoi = defaultdict(int)
    context_length = 5
    
    for dataset_name, _ in datasets_info:
        subset_file = f'{base_path}/mlp_dataset/{dataset_name}_subset.txt'
        if os.path.exists(subset_file):
            try:
                # Process the subset file to build vocabulary
                pairs = list(create_context_target_pairs(subset_file, context_length, stoi, max_words=100000))
                for context, target in pairs:
                    pass  # Just process to build vocab, don't need the pairs
            except Exception:
                pass  # Silently skip if file doesn't exist or can't be processed
    
    # Create inverse mapping
    itos = {i: w for w, i in stoi.items()}
    return dict(stoi), itos


@st.cache_resource
def load_model(
    category: str,
    embedding_dim: int,
    hidden_layers: int,
    activation: str
) -> Optional[MLPTextGenerator]:
    """
    Load a trained model.
    
    Args:
        category: 'structured' or 'unstructured'
        embedding_dim: Embedding dimension (32 or 64)
        hidden_layers: Number of hidden layers (1 or 2)
        activation: Activation function ('relu' or 'tanh')
    
    Returns:
        Loaded model or None if not found
    """
    base_path = './struct_model' if category == 'structured' else './unstruct_model'
    
    model_name = f'emb{embedding_dim}_hidden{hidden_layers}_{activation}'
    model_path = f'{base_path}/{model_name}.pth'
    
    if not os.path.exists(model_path):
        st.error(f"Model file not found: {model_path}")
        return None
    
    try:
        checkpoint = torch.load(model_path, map_location='cpu', weights_only=False)
        
        # Determine vocab size from the checkpoint (embedding weight shape)
        vocab_size = checkpoint['model_state_dict']['embedding.weight'].shape[0]
        
        config = load_model_config()
        hidden_dims = [1024] * hidden_layers
        
        model = MLPTextGenerator(
            vocab_size,
            embedding_dim,
            config['context_length'],
            hidden_dims,
            activation
        )
        model.load_state_dict(checkpoint['model_state_dict'])
        return model
    except Exception as e:
        st.error(f"Error loading model: {e}")
        import traceback
        traceback.print_exc()
        return None


@st.cache_data
def compute_tsne_embeddings(embeddings: np.ndarray, perplexity: int = 30) -> np.ndarray:
    """
    Compute t-SNE embeddings for visualization.
    
    Args:
        embeddings: Word embeddings (vocab_size, embedding_dim)
        perplexity: t-SNE perplexity parameter
    
    Returns:
        2D t-SNE embeddings (vocab_size, 2)
    """
    tsne = TSNE(n_components=2, random_state=42, perplexity=min(perplexity, embeddings.shape[0] - 1))
    return tsne.fit_transform(embeddings)


def visualize_embeddings_tsne(
    model,
    stoi: Dict,
    itos: Dict,
    num_words: int = 100
):
    """
    Create interactive t-SNE visualization of word embeddings.
    
    Args:
        model: Trained MLPTextGenerator
        stoi: String-to-index mapping
        itos: Index-to-string mapping
        num_words: Number of most frequent words to visualize
    """
    st.subheader("📊 Word Embeddings t-SNE Visualization")
    
    # Get embeddings from model
    model.eval()
    with torch.no_grad():
        embeddings = model.embedding.weight.detach().cpu().numpy()
    
    # Select top words by vocabulary index (most frequent are typically earlier)
    num_to_show = min(num_words, len(stoi) - 2)  # Exclude <PAD> and <UNK>
    word_indices = list(range(2, min(num_to_show + 2, len(stoi))))
    
    selected_embeddings = embeddings[word_indices]
    word_labels = [itos.get(idx, f'<UNK_{idx}>') for idx in word_indices]
    
    # Compute t-SNE
    with st.spinner("Computing t-SNE embeddings..."):
        embeddings_2d = compute_tsne_embeddings(selected_embeddings, perplexity=30)
    
    # Create interactive Plotly visualization
    fig = go.Figure()
    
    fig.add_trace(go.Scatter(
        x=embeddings_2d[:, 0],
        y=embeddings_2d[:, 1],
        mode='markers+text',
        text=word_labels,
        textposition='top center',
        textfont=dict(color='white', size=11),
        marker=dict(
            size=8,
            # color=list(range(len(word_labels))),
            # colorscale='Viridis',
            showscale=False,
            opacity=0.8,
            line=dict(width=0.5, color='white')
        ),
        customdata=[f"<b>{word}</b>" for word in word_labels],
        hovertemplate='%{customdata}<extra></extra>',
        showlegend=False
    ))
    
    fig.update_layout(
        title=f"t-SNE Visualization of Top {num_to_show} Word Embeddings",
        xaxis_title="t-SNE Dimension 1",
        yaxis_title="t-SNE Dimension 2",
        width=900,
        height=700,
        hovermode='closest',
        # plot_bgcolor='rgba(240,240,240,0.9)',
        showlegend=False,
        font=dict(size=10)
    )
    
    st.plotly_chart(fig, use_container_width=True)
    
    # Display statistics
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Words Visualized", num_to_show)
    with col2:
        st.metric("Embedding Dim", embeddings.shape[1])
    with col3:
        st.metric("Total Vocabulary", len(stoi))


def visualize_loss_curves_comparison(
    category_key: str,
    selected_models: List[str]
):
    """
    Create interactive comparison of loss curves for multiple models.
    
    Args:
        category_key: 'unstructured' or 'structured'
        selected_models: List of model names (e.g., ['emb32_hidden1_relu', 'emb64_hidden2_tanh'])
    """
    st.subheader("📉 Loss Curve Comparison")
    
    if not selected_models:
        st.warning("Please select at least one model to compare")
        return
    
    # Load loss data for all selected models
    loss_data = {}
    base_path = './struct_model' if category_key == 'structured' else './unstruct_model'
    
    for model_name in selected_models:
        loss_file = f"{base_path}/{model_name}_loss.pth"
        try:
            data = torch.load(loss_file, map_location='cpu', weights_only=False)
            loss_data[model_name] = data
        except Exception as e:
            st.warning(f"Could not load loss data for {model_name}: {e}")
    
    if not loss_data:
        st.error("No loss data could be loaded for the selected models")
        return
    
    # Create comparison figure with subplots
    fig = go.Figure()
    
    # Define colors for different models
    colors = [
        '#1f77b4', '#ff7f0e', '#2ca02c', '#d62728',
        '#9467bd', '#8c564b', '#e377c2', '#7f7f7f'
    ]
    
    epochs = range(1, len(loss_data[list(loss_data.keys())[0]]['train_losses']) + 1)
    
    # Add traces for each model
    for idx, (model_name, data) in enumerate(loss_data.items()):
        color = colors[idx % len(colors)]
        
        # Training loss
        fig.add_trace(go.Scatter(
            x=list(epochs),
            y=data['train_losses'],
            mode='lines',
            name=f"{model_name} (Train)",
            line=dict(color=color, width=2),
            hovertemplate='<b>%{fullData.name}</b><br>Epoch: %{x}<br>Loss: %{y:.6f}<extra></extra>'
        ))
        
        # Validation loss
        fig.add_trace(go.Scatter(
            x=list(epochs),
            y=data['val_losses'],
            mode='lines',
            name=f"{model_name} (Val)",
            line=dict(color=color, width=2, dash='dash'),
            hovertemplate='<b>%{fullData.name}</b><br>Epoch: %{x}<br>Loss: %{y:.6f}<extra></extra>'
        ))
    
    fig.update_layout(
        title="Training and Validation Loss Comparison",
        xaxis_title="Epoch",
        yaxis_title="Loss",
        hovermode='x unified',
        width=1000,
        height=600,
        font=dict(size=11),
        legend=dict(
            x=1.02,
            y=1,
            xanchor='left',
            yanchor='top'
        )
    )
    
    st.plotly_chart(fig, use_container_width=True)
    
    # Create accuracy comparison figure
    fig_acc = go.Figure()
    
    for idx, (model_name, data) in enumerate(loss_data.items()):
        color = colors[idx % len(colors)]
        
        fig_acc.add_trace(go.Scatter(
            x=list(epochs),
            y=data['val_accuracies'],
            mode='lines',
            name=model_name,
            line=dict(color=color, width=2),
            hovertemplate='<b>%{fullData.name}</b><br>Epoch: %{x}<br>Accuracy: %{y:.4f}<extra></extra>'
        ))
    
    fig_acc.update_layout(
        title="Validation Accuracy Comparison",
        xaxis_title="Epoch",
        yaxis_title="Validation Accuracy",
        hovermode='x unified',
        width=1000,
        height=600,
        font=dict(size=11),
        legend=dict(
            x=1.02,
            y=1,
            xanchor='left',
            yanchor='top'
        )
    )
    
    st.plotly_chart(fig_acc, use_container_width=True)
    
    # Display statistics table
    st.subheader("📊 Model Statistics")
    
    stats_data = []
    for model_name, data in loss_data.items():
        stats_data.append({
            "Model": model_name,
            "Initial Train Loss": f"{data['train_losses'][0]:.6f}",
            "Final Train Loss": f"{data['train_losses'][-1]:.6f}",
            "Initial Val Loss": f"{data['val_losses'][0]:.6f}",
            "Final Val Loss": f"{data['val_losses'][-1]:.6f}",
            "Best Val Accuracy": f"{max(data['val_accuracies']):.4f}",
            "Final Val Accuracy": f"{data['val_accuracies'][-1]:.4f}",
            "Total Epochs": len(data['train_losses'])
        })
    
    import pandas as pd
    stats_df = pd.DataFrame(stats_data)
    st.dataframe(stats_df, use_container_width=True)


def main():
    """Main Streamlit application."""
    
    # Page configuration
    st.set_page_config(
        page_title="Next Word Prediction",
        page_icon="📝",
        layout="wide",
        initial_sidebar_state="expanded"
    )
    
    st.title("🚀 Next Word Prediction with MLP Language Models")
    
    # Add page selector
    page = st.selectbox(
        "Select Page",
        options=["Text Prediction", "Embedding Visualization", "HTML Visualizations", "Loss Curve Comparison"],
        index=0
    )
    
    st.markdown("""
    This application uses trained MLP models to predict the next words in a given context.
    You can control prediction behavior with various parameters and strategies.
    
    **Key Features:**
    - Select from pre-trained model variants
    - Temperature-based sampling for controlled randomness
    - Out-of-vocabulary (OOV) word handling strategies
    - Real-time prediction with confidence scores
    - Visualize word embeddings with t-SNE
    - Interactive HTML visualizations of embeddings and clusters
    """)
    
    # Sidebar configuration
    st.sidebar.header("⚙️ Configuration")
    
    # Dataset category selection
    category = st.sidebar.radio(
        "Dataset Category",
        options=['Unstructured (Essays, Literature)', 'Structured (Code, Math)'],
        index=0,
        help="Choose between natural language datasets or technical/structured content"
    )
    category_key = 'unstructured' if 'Unstructured' in category else 'structured'
    
    # Model hyperparameters
    st.sidebar.subheader("Model Parameters")
    
    embedding_dim = st.sidebar.select_slider(
        "Embedding Dimension",
        options=[32, 64],
        value=32,
        help="Size of word embedding vectors (32 or 64)"
    )
    
    hidden_layers = st.sidebar.select_slider(
        "Number of Hidden Layers",
        options=[1, 2],
        value=2,
        help="Number of hidden layers in the MLP (1 or 2)"
    )
    
    activation = st.sidebar.radio(
        "Activation Function",
        options=['relu', 'tanh'],
        index=1,
        help="Activation function between hidden layers"
    )
    
    # Prediction parameters
    st.sidebar.subheader("Prediction Parameters")
    
    context_length = st.sidebar.slider(
        "Context Length",
        min_value=1,
        max_value=10,
        value=5,
        help="Number of words to use as context for prediction"
    )
    
    num_predictions = st.sidebar.slider(
        "Number of Words to Predict",
        min_value=1,
        max_value=20,
        value=5,
        help="How many words to predict after the context"
    )
    
    temperature = st.sidebar.slider(
        "Temperature",
        min_value=0.1,
        max_value=2.0,
        value=1.0,
        step=0.1,
        help="""Controls randomness in predictions:
        - <1.0: More deterministic (always pick best)
        - 1.0: Normal probability distribution
        - >1.0: More random and creative"""
    )
    
    oov_strategy = st.sidebar.selectbox(
        "Out-of-Vocabulary (OOV) Handling",
        options=['skip', 'unk', 'similar'],
        help="""How to handle words not in vocabulary:
        - skip: Ignore OOV words
        - unk: Use <UNK> token
        - similar: Use most similar word in vocabulary"""
    )
    
    random_seed = st.sidebar.number_input(
        "Random Seed",
        min_value=0,
        max_value=2**31 - 1,
        value=42,
        step=1,
        help="Set to 0 for random behavior each time"
    )
    seed_for_prediction = random_seed if random_seed != 0 else None
    
    # PAGE 1: TEXT PREDICTION
    if page == "Text Prediction":
        # Main content area
        st.header("📋 Input Text")
        
        # Example texts for different categories
        example_texts = {
            'unstructured': "First person says that",
            'structured': "if ( x > 0 ) {"
        }
        
        example_text = example_texts.get(category_key, "")
        
        user_input = st.text_area(
            "Enter text to predict from:",
            value=example_text,
            height=100,
            placeholder="Enter your text here...",
            help="The model will predict the next words after this text"
        )
        
        # Load model and make predictions
        col1, col2, col3 = st.columns(3)
        
        with col1:
            predict_button = st.button("🎯 Predict Next Words", use_container_width=True)
        
        with col2:
            confidence_toggle = st.checkbox("Show Confidence Scores", value=True)
        
        with col3:
            clear_button = st.button("🔄 Clear Input", use_container_width=True)
        
        if clear_button:
            st.rerun()
        
        if predict_button and user_input.strip():
            try:
                # Load model and vocabulary
                with st.spinner("Loading model..."):
                    model = load_model(category_key, embedding_dim, hidden_layers, activation)
                    if model is None:
                        st.error("Failed to load model")
                        return
                    
                    stoi, itos = load_vocab(category_key)
                
                # Prepare context
                words = user_input.lower().strip().split()
                if not words:
                    st.error("Please enter some text")
                    return
                
                # Create prediction engine
                device = 'cuda' if torch.cuda.is_available() else 'cpu'
                vocab_manager = VocabularyManager(stoi, itos)
                prediction_engine = TextPredictionEngine(
                    model, vocab_manager, context_length=5, device=device
                )
                
                # Predict next words
                with st.spinner("Generating predictions..."):
                    predictions = prediction_engine.predict_next_words(
                        words[-context_length:],
                        num_words=num_predictions,
                        temperature=temperature,
                        oov_strategy=oov_strategy,
                        seed=seed_for_prediction
                    )
                
                # Display results
                st.header("🎲 Predictions")
                
                # Display input context
                st.subheader("Context")
                st.info(f"**Last {min(len(words), context_length)} words:** {' → '.join(words[-context_length:])}")
                
                # Display predictions
                st.subheader("Predicted Next Words")
                
                if confidence_toggle:
                    # Get predictions with confidence
                    predictions_conf = prediction_engine.predict_with_confidence(
                        words[-context_length:],
                        num_words=num_predictions,
                        temperature=temperature,
                        oov_strategy=oov_strategy,
                        seed=seed_for_prediction,
                        top_k=3
                    )
                    
                    # Create a nicely formatted display
                    prediction_text = []
                    cols = st.columns(len(predictions))
                    
                    for i, (word, conf) in enumerate(predictions_conf):
                        with cols[i]:
                            st.metric(
                                f"Position {i+1}",
                                value=word,
                                delta=f"{conf:.2%} confidence"
                            )
                            prediction_text.append(word)
                else:
                    # Simple display
                    prediction_text = predictions
                    
                    cols = st.columns(len(predictions))
                    for i, word in enumerate(predictions):
                        with cols[i]:
                            st.markdown(f"### {i+1}. {word}")
                
                # Show full sentence
                st.subheader("Complete Text")
                complete_text = user_input.strip() + " " + " ".join(prediction_text)
                st.success(complete_text)
                
                # Show model info
                with st.expander("📊 Model Information"):
                    col1, col2, col3, col4 = st.columns(4)
                    with col1:
                        st.metric("Embedding Dim", embedding_dim)
                    with col2:
                        st.metric("Hidden Layers", hidden_layers)
                    with col3:
                        st.metric("Activation", activation)
                    with col4:
                        st.metric("Temperature", f"{temperature:.1f}")
                    
                    st.write(f"**Context Length:** {context_length}")
                    st.write(f"**OOV Strategy:** {oov_strategy}")
                    st.write(f"**Device:** {device}")
                    st.write(f"**Vocabulary Size:** {len(stoi)}")
                
                # Show OOV analysis
                vocab_manager = VocabularyManager(stoi, itos)
                oov_words = [w for w in words if vocab_manager.is_oov(w)]
                
                if oov_words:
                    with st.expander("⚠️ Out-of-Vocabulary Words Found"):
                        st.warning(f"The following words are not in the vocabulary: {', '.join(oov_words)}")
                        st.info(f"Using '{oov_strategy}' strategy to handle these words")
            
            except Exception as e:
                st.error(f"An error occurred: {e}")
                import traceback
                st.error(traceback.format_exc())
    
    # PAGE 2: EMBEDDING VISUALIZATION
    elif page == "Embedding Visualization":
        st.header("🎨 Word Embedding Visualization")
        
        st.markdown("""
        Visualize the word embeddings learned by the selected model using t-SNE dimensionality reduction.
        
        t-SNE (t-Distributed Stochastic Neighbor Embedding) projects high-dimensional embeddings into 
        2D space while preserving local neighborhood structure. Similar words appear close together.
        """)
        
        # Load model and vocabulary
        try:
            with st.spinner("Loading model..."):
                model = load_model(category_key, embedding_dim, hidden_layers, activation)
                if model is None:
                    st.error("Failed to load model")
                    return
                
                stoi, itos = load_vocab(category_key)
            
            # Number of words to visualize
            num_words_viz = st.slider(
                "Number of Words to Visualize",
                min_value=20,
                max_value=500,
                value=100,
                step=20,
                help="More words = more detailed but slower to compute"
            )
            
            # Show visualization
            visualize_embeddings_tsne(model, stoi, itos, num_words=num_words_viz)
            
            # Show selected model info
            with st.expander("ℹ️ Model Information"):
                col1, col2, col3, col4 = st.columns(4)
                with col1:
                    st.metric("Embedding Dim", embedding_dim)
                with col2:
                    st.metric("Hidden Layers", hidden_layers)
                with col3:
                    st.metric("Activation", activation)
                with col4:
                    st.metric("Total Vocabulary", len(stoi))
                
                st.write("**Model Name:**", f"emb{embedding_dim}_hidden{hidden_layers}_{activation}")
                st.write("**Category:**", category)
                
            # Explanation
            with st.expander("📖 How to Read the Visualization"):
                st.markdown("""
                **What each element represents:**
                
                - **Dots**: Individual words from the vocabulary
                - **Position**: Two dimensions computed by t-SNE
                  - Similar words appear **close together**
                  - Dissimilar words appear **far apart**
                - **Color**: Applied for visual distinction (no specific meaning)
                - **Labels**: Word text for easy identification
                
                **Patterns to look for:**
                
                1. **Semantic Clusters**: Related words grouped together
                   - For unstructured: "king", "queen", "prince" might cluster
                   - For structured: "(", ")", "{", "}" might cluster
                
                2. **Distance Relationships**: 
                   - Words that appear in similar contexts are close
                   - Words with opposite meanings are far apart
                
                3. **Embedding Quality**: Well-separated clusters indicate good embeddings
                
                **Hover over words** to see their names clearly.
                """)
        
        except Exception as e:
            st.error(f"An error occurred: {e}")
            import traceback
            st.error(traceback.format_exc())
    
    # PAGE 3: HTML VISUALIZATIONS
    elif page == "HTML Visualizations":
        st.header("📊 Interactive HTML Visualizations")
        
        st.markdown("""
        This page provides links to pre-generated interactive HTML visualizations from the project.
        These visualizations show embeddings, clusters, and model analysis from the notebook experiments.
        """)
        
        # Define available HTML visualizations
        html_files = {
            "Elbow Curve": {
                "file": "elbow_curve.html",
                "description": "Elbow method for determining optimal number of clusters"
            },
            "PCA Variance Explained": {
                "file": "pca_variance_explained.html",
                "description": "PCA analysis showing variance explained by principal components"
            },
            "t-SNE Best model for category 1": {
                "file": "tsne_embeddings_2d.html",
                "description": "2D t-SNE visualization of all word embeddings"
            },
            "t-SNE Best model for category 2": {
                "file": "tsne_embeddings_2d_struct.html",
                "description": "2D t-SNE visualization for structured text model"
            },
            "t-SNE Clustered": {
                "file": "tsne_clustered_detailed.html",
                "description": "Detailed t-SNE visualization with cluster annotations"
            },
            "t-SNE Clustered (Structured)": {
                "file": "tsne_clustered_struct.html",
                "description": "t-SNE clustering visualization for structured text"
            },
            "t-SNE comparison across models cat 1": {
                "file": "tsne_clustered_comparison.html",
                "description": "Side-by-side comparison of clustered embeddings"
            },
            "t-SNE comparison across models cat 2": {
                "file": "tsne_clustered_struct_comparison.html",
                "description": "Comparison of structured text embedding clusters"
            },
            "t-SNE Struct Embedding Comparison": {
                "file": "tsne_embeddings_struct_comparison.html",
                "description": "Comparison of structured text embeddings"
            }
        }
        
        # Create tabs for different visualization categories
        tab1, tab2, tab3 = st.tabs(["Overview", "t-SNE Visualizations", "Analysis Visualizations"])
        
        with tab1:
            st.subheader("Available Visualizations")
            st.info(f"📁 Total visualizations available: {len(html_files)}")
            
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown("**t-SNE Visualizations:**")
                st.markdown("- t-SNE Best model for category 1")
                st.markdown("- t-SNE Best model for category 2")
                st.markdown("- t-SNE Clustered")
                st.markdown("- t-SNE Clustered (Structured)")
                st.markdown("- t-SNE comparison across models cat 1")
                st.markdown("- t-SNE comparison across models cat 2")
            
            with col2:
                st.markdown("**Analysis Visualizations:**")
                st.markdown("- PCA Variance Explained")
                st.markdown("- Elbow Curve")
            
            st.markdown("---")
            st.markdown("""
            **How to use these visualizations:**
            
            1. Click on the visualization tabs above
            2. Select a visualization to view
            3. Use the interactive features:
               - **Hover** over points to see details
               - **Zoom** by dragging the mouse
               - **Pan** to move around
               - **Double-click** to reset the view
            4. **Download** visualizations using the camera icon in the top-right corner
            """)
        
        with tab2:
            st.subheader("t-SNE Embedding Visualizations")
            
            viz_selection = st.selectbox(
                "Select t-SNE Visualization",
                options=[
                    "t-SNE Best model for category 1",
                    "t-SNE Best model for category 2",
                    "t-SNE Clustered",
                    "t-SNE Clustered (Structured)",
                    "t-SNE comparison across models cat 1",
                    "t-SNE comparison across models cat 2",
                ],
                key="tsne_select"
            )
            
            if viz_selection in html_files:
                info = html_files[viz_selection]
                file_path = info["file"]
                
                st.markdown(f"**Description:** {info['description']}")
                
                try:
                    # Try to read and display the HTML file
                    with open(file_path, 'r', encoding='utf-8') as f:
                        html_content = f.read()
                    
                    # Use Streamlit's HTML component to embed the visualization
                    st.components.v1.html(html_content, height=700, scrolling=True)
                    
                    # Provide download link
                    with open(file_path, 'rb') as f:
                        st.download_button(
                            label="📥 Download HTML",
                            data=f.read(),
                            file_name=file_path,
                            mime="text/html"
                        )
                
                except FileNotFoundError:
                    st.error(f"❌ File not found: {file_path}")
                    st.info("This visualization may not have been generated yet.")
                except Exception as e:
                    st.error(f"❌ Error loading visualization: {e}")
        
        with tab3:
            st.subheader("Analysis Visualizations")
            
            viz_selection = st.selectbox(
                "Select Analysis Visualization",
                options=[
                    "Elbow Curve",
                    "PCA Variance Explained"
                ],
                key="analysis_select"
            )
            
            if viz_selection in html_files:
                info = html_files[viz_selection]
                file_path = info["file"]
                
                st.markdown(f"**Description:** {info['description']}")
                
                try:
                    # Try to read and display the HTML file
                    with open(file_path, 'r', encoding='utf-8') as f:
                        html_content = f.read()
                    
                    # Use Streamlit's HTML component to embed the visualization
                    st.components.v1.html(html_content, height=700, scrolling=True)
                    
                    # Provide download link
                    with open(file_path, 'rb') as f:
                        st.download_button(
                            label="📥 Download HTML",
                            data=f.read(),
                            file_name=file_path,
                            mime="text/html"
                        )
                
                except FileNotFoundError:
                    st.error(f"❌ File not found: {file_path}")
                    st.info("This visualization may not have been generated yet.")
                except Exception as e:
                    st.error(f"❌ Error loading visualization: {e}")
    
    # PAGE 4: LOSS CURVE COMPARISON
    elif page == "Loss Curve Comparison":
        st.header("📉 Model Loss Curve Comparison")
        
        st.markdown("""
        Compare training and validation loss curves across different model variants.
        This helps identify which model configurations perform better and converge faster.
        
        **What to look for:**
        - **Lower final loss** = better model performance
        - **Smooth curves** = stable training
        - **Convergence speed** = how quickly loss plateaus
        - **Validation accuracy** = generalization performance
        """)
        
        # Model selection UI
        st.subheader("🔧 Select Models to Compare")
        
        # Available models based on hyperparameters
        embedding_options = [32, 64]
        hidden_options = [1, 2]
        activation_options = ['relu', 'tanh']
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            select_all_emb = st.checkbox("All Embeddings", value=False, key="emb_all")
            if select_all_emb:
                selected_embs = embedding_options
            else:
                selected_embs = st.multiselect(
                    "Embedding Dimensions",
                    options=embedding_options,
                    default=[32]
                )
        
        with col2:
            select_all_hidden = st.checkbox("All Hidden Layers", value=False, key="hidden_all")
            if select_all_hidden:
                selected_hiddens = hidden_options
            else:
                selected_hiddens = st.multiselect(
                    "Hidden Layers",
                    options=hidden_options,
                    default=[2]
                )
        
        with col3:
            select_all_act = st.checkbox("All Activations", value=False, key="act_all")
            if select_all_act:
                selected_acts = activation_options
            else:
                selected_acts = st.multiselect(
                    "Activation Functions",
                    options=activation_options,
                    default=['relu']
                )
        
        # Generate list of models based on selections
        available_models = []
        for emb in selected_embs:
            for hidden in selected_hiddens:
                for act in selected_acts:
                    model_name = f"emb{emb}_hidden{hidden}_{act}"
                    available_models.append(model_name)
        
        # Manual model selection with checkboxes
        st.subheader("📋 Select Specific Models")
        
        selected_models = []
        
        cols_per_row = 3
        cols = st.columns(cols_per_row)
        
        for i, model_name in enumerate(available_models):
            col_idx = i % cols_per_row
            with cols[col_idx]:
                if st.checkbox(model_name, value=(i < 2)):  # Default select first 2
                    selected_models.append(model_name)
        
        # Visualization button and results
        if st.button("📊 Generate Comparison", use_container_width=True):
            if not selected_models:
                st.error("Please select at least one model")
            else:
                try:
                    with st.spinner("Loading loss data and generating visualization..."):
                        visualize_loss_curves_comparison(category_key, selected_models)
                    
                    # Additional analysis section
                    with st.expander("📈 Detailed Analysis"):
                        st.markdown("""
                        **How to interpret the plots:**
                        
                        1. **Loss Curves:**
                           - Solid lines = Training loss
                           - Dashed lines = Validation loss
                           - Lower is better
                        
                        2. **Accuracy Curves:**
                           - Shows validation accuracy over epochs
                           - Higher is better
                           - Plateau = model has converged
                        
                        3. **Best Practice Indicators:**
                           - Small gap between train and val loss = good generalization
                           - Large gap = overfitting
                           - Smooth curves = stable learning
                        """)
                
                except Exception as e:
                    st.error(f"An error occurred: {e}")
                    import traceback
                    st.error(traceback.format_exc())


if __name__ == "__main__":
    main()
