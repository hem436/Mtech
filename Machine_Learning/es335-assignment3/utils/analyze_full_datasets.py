#!/usr/bin/env python3

import os
import random
import re
from collections import Counter

def analyze_full_datasets():
    """Analyze the full datasets without subsetting to understand their size"""
    
    datasets = [
        ('category1/enwik9', 'Wikipedia', True),
        ('category1/shakespeare_input.txt', 'Shakespeare', True),
        ('category1/paul_graham_essays.txt', 'Paul Graham Essays', True),
        ('category1/warpeace_input.txt', 'War and Peace', True),
        ('category1/input.txt', 'Generic Input', True),
        ('category2/sklearn_docs.txt', 'Sklearn Docs', False),
        ('category2/stacks.txt', 'Stacks/LaTeX', False),
        ('category2/linux_input.txt', 'Linux Code', False),
    ]
    
    print("FULL DATASET ANALYSIS")
    print("=" * 60)
    
    results = []
    
    for filepath, name, is_natural in datasets:
        if not os.path.exists(filepath):
            print(f"❌ {name}: File not found - {filepath}")
            continue
            
        try:
            # Get file size
            file_size = os.path.getsize(filepath)
            print(f"\n📁 {name}")
            print(f"   File: {filepath}")
            print(f"   Size: {file_size:,} bytes ({file_size/1024/1024:.1f} MB)")
            
            # Read a sample to estimate content
            with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
                if file_size > 50 * 1024 * 1024:  # > 5MB
                    sample_text = f.read(50*1024 * 1024)  # Read 1MB sample
                    print("   📊 Analysis based on 50MB sample")
                else:
                    sample_text = f.read()
                    print("   📊 Analysis of full file")
            
            # Basic preprocessing
            if is_natural:
                clean_text = re.sub(r'[^a-zA-Z0-9 \.]', '', sample_text)
                sentences = [s.strip() for s in clean_text.split('.') if s.strip() and len(s.strip()) > 10]
            else:
                clean_text = re.sub(r'[^\w\s\.\,\;\:\(\)\[\]\{\}\"\'\_\-\+\=\>\<\#]', '', sample_text)
                sentences = [s.strip() for s in clean_text.split('\n') if s.strip() and len(s.strip()) > 5]
            
            # Calculate statistics
            word_counts = Counter()
            total_words = 0
            for sentence in sentences:
                words = sentence.split()
                word_counts.update(words)
                total_words += len(words)
            
            # Estimate full dataset size
            if file_size > 1024 * 1024:  # If we sampled
                estimate_factor = file_size / len(sample_text)
                estimated_sentences = int(len(sentences) * estimate_factor)
                estimated_words = int(total_words * estimate_factor)
                estimated_vocab = int(len(word_counts) * (estimate_factor ** 0.7))  # Vocab grows slower
            else:
                estimated_sentences = len(sentences)
                estimated_words = total_words
                estimated_vocab = len(word_counts)
            
            print(f"   📈 Estimated sentences: {estimated_sentences:,}")
            print(f"   📝 Estimated words: {estimated_words:,}")
            print(f"   📚 Estimated vocabulary: {estimated_vocab:,}")
            print(f"   📊 Avg words/sentence: {estimated_words/max(1,estimated_sentences):.1f}")
            
            # Most common words
            top_words = word_counts.most_common(5)
            print(f"   🔤 Top words: {top_words}")
            
            results.append({
                'name': name,
                'filepath': filepath,
                'is_natural': is_natural,
                'file_size_mb': file_size / 1024 / 1024,
                'estimated_sentences': estimated_sentences,
                'estimated_words': estimated_words,
                'estimated_vocab': estimated_vocab,
                'avg_words_per_sentence': estimated_words/max(1,estimated_sentences)
            })
            
        except Exception as e:
            print(f"❌ Error analyzing {name}: {e}")
    
    # Summary recommendations
    print(f"\n{'='*60}")
    print("RECOMMENDED SUBSET SIZES FOR MLP TRAINING")
    print(f"{'='*60}")
    
    for result in results:
        name = result['name']
        sentences = result['estimated_sentences']
        
        # Recommend subset size based on dataset characteristics
        if sentences < 1000:
            recommended = sentences  # Use all
        elif sentences < 5000:
            recommended = min(1500, sentences)
        elif sentences < 20000:
            recommended = min(2500, sentences) 
        else:
            recommended = min(3000, sentences)
        
        category = "Natural Language" if result['is_natural'] else "Structured Text"
        print(f"📋 {name} ({category})")
        print(f"   Available: {sentences:,} sentences")
        print(f"   Recommended subset: {recommended:,} sentences")
        print(f"   Reason: {'Use all data' if recommended == sentences else f'Manageable size for training'}")
        print()

if __name__ == "__main__":
    analyze_full_datasets()