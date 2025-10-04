# Enhanced visualization code for descriptor matches
# Copy and paste these functions into new cells in your notebook

# Cell 1: Enhanced Descriptor Matches Visualization
def visualize_descriptor_matches(img1, img2, keypoints1, keypoints2, matches, max_matches=50):
    """
    Visualize descriptor matches between two images with connecting lines
    
    Args:
        img1, img2: Input images
        keypoints1, keypoints2: Keypoints for each image
        matches: Array of match indices [(idx1, idx2), ...]
        max_matches: Maximum number of matches to display
    """
    # Limit matches for cleaner visualization
    if len(matches) > max_matches:
        matches = matches[:max_matches]
    
    # Create side-by-side image
    h1, w1 = img1.shape[:2]
    h2, w2 = img2.shape[:2]
    
    # Make heights equal
    max_height = max(h1, h2)
    
    # Create canvas
    canvas = np.zeros((max_height, w1 + w2, 3), dtype=img1.dtype)
    
    # Place images
    canvas[:h1, :w1] = img1
    canvas[:h2, w1:w1+w2] = img2
    
    # Create figure
    fig, ax = plt.subplots(1, 1, figsize=(16, 8))
    ax.imshow(canvas)
    
    # Plot keypoints and matches
    colors = plt.cm.rainbow(np.linspace(0, 1, len(matches)))
    
    for idx, ((i, j), color) in enumerate(zip(matches, colors)):
        # Get coordinates
        y1, x1 = keypoints1[i]
        y2, x2 = keypoints2[j]
        
        # Adjust x2 for second image position
        x2_adj = x2 + w1
        
        # Plot keypoints
        ax.plot(x1, y1, 'o', color=color, markersize=8, markeredgecolor='white', markeredgewidth=1)
        ax.plot(x2_adj, y2, 'o', color=color, markersize=8, markeredgecolor='white', markeredgewidth=1)
        
        # Draw connecting line
        ax.plot([x1, x2_adj], [y1, y2], '-', color=color, linewidth=2, alpha=0.7)
    
    ax.set_title(f'Descriptor Matches Visualization ({len(matches)} matches)', fontsize=14, fontweight='bold')
    ax.axis('off')
    
    # Add image labels
    ax.text(w1//2, -20, 'Mosaic Image', ha='center', fontsize=12, fontweight='bold')
    ax.text(w1 + w2//2, -20, 'Key Image', ha='center', fontsize=12, fontweight='bold')
    
    plt.tight_layout()
    plt.show()
    
    return canvas

# Run the visualization
print("ORB Descriptor Matches:")
visualize_descriptor_matches(mosaic_rgb_rs, key_rgb, keypoints1, keypoints2, matches, max_matches=30)

# ================================================================================================

# Cell 2: Numbered Matches Visualization
def show_numbered_matches(img1, img2, keypoints1, keypoints2, matches, num_matches=20):
    """
    Show matches with numbered keypoints for easier identification
    """
    # Limit matches
    if len(matches) > num_matches:
        matches = matches[:num_matches]
    
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(16, 8))
    
    # Show first image with numbered keypoints
    ax1.imshow(img1)
    ax1.set_title('Mosaic Image - Matched Keypoints', fontsize=12, fontweight='bold')
    ax1.axis('off')
    
    # Show second image with numbered keypoints
    ax2.imshow(img2)
    ax2.set_title('Key Image - Matched Keypoints', fontsize=12, fontweight='bold')
    ax2.axis('off')
    
    # Plot numbered matches
    for idx, (i, j) in enumerate(matches):
        y1, x1 = keypoints1[i]
        y2, x2 = keypoints2[j]
        
        # Use same color for corresponding points
        color = plt.cm.tab10(idx % 10)
        
        # Plot keypoints with numbers
        ax1.plot(x1, y1, 'o', color=color, markersize=10, markeredgecolor='white', markeredgewidth=2)
        ax1.text(x1+3, y1-3, str(idx+1), color='white', fontsize=8, fontweight='bold')
        
        ax2.plot(x2, y2, 'o', color=color, markersize=10, markeredgecolor='white', markeredgewidth=2)
        ax2.text(x2+3, y2-3, str(idx+1), color='white', fontsize=8, fontweight='bold')
    
    plt.tight_layout()
    plt.show()

# Run numbered matches
print("Numbered Keypoint Matches:")
show_numbered_matches(mosaic_rgb_rs, key_rgb, keypoints1, keypoints2, matches, num_matches=15)

# ================================================================================================

# Cell 3: Match Quality Analysis
def analyze_match_quality(keypoints1, keypoints2, matches, descriptors1, descriptors2):
    """
    Analyze the quality of matches based on descriptor distances
    """
    distances = []
    
    for i, j in matches:
        # Calculate Hamming distance for ORB descriptors
        dist = np.sum(descriptors1[i] != descriptors2[j])
        distances.append(dist)
    
    distances = np.array(distances)
    
    print(f"Match Quality Statistics:")
    print(f"Total matches: {len(matches)}")
    print(f"Mean distance: {distances.mean():.2f}")
    print(f"Std distance: {distances.std():.2f}")
    print(f"Min distance: {distances.min()}")
    print(f"Max distance: {distances.max()}")
    
    # Plot distance distribution
    plt.figure(figsize=(10, 4))
    plt.subplot(1, 2, 1)
    plt.hist(distances, bins=20, alpha=0.7, edgecolor='black')
    plt.xlabel('Hamming Distance')
    plt.ylabel('Number of Matches')
    plt.title('Distribution of Match Distances')
    plt.grid(True, alpha=0.3)
    
    # Show best matches (lowest distances)
    best_matches_idx = np.argsort(distances)[:10]
    plt.subplot(1, 2, 2)
    plt.plot(range(len(distances)), sorted(distances), 'b-', alpha=0.7)
    plt.scatter(range(10), sorted(distances)[:10], color='red', s=50, zorder=5)
    plt.xlabel('Match Rank')
    plt.ylabel('Hamming Distance')
    plt.title('Matches Sorted by Quality')
    plt.grid(True, alpha=0.3)
    
    plt.tight_layout()
    plt.show()
    
    return distances, best_matches_idx

# Analyze match quality
distances, best_match_indices = analyze_match_quality(keypoints1, keypoints2, matches, descriptors1, descriptors2)

# ================================================================================================

# Cell 4: Best Quality Matches Visualization
def show_best_matches(img1, img2, keypoints1, keypoints2, matches, distances, top_n=10):
    """
    Visualize only the best quality matches
    """
    # Get indices of best matches
    best_indices = np.argsort(distances)[:top_n]
    best_matches = matches[best_indices]
    best_distances = distances[best_indices]
    
    # Create side-by-side visualization
    h1, w1 = img1.shape[:2]
    h2, w2 = img2.shape[:2]
    max_height = max(h1, h2)
    canvas = np.zeros((max_height, w1 + w2, 3), dtype=img1.dtype)
    canvas[:h1, :w1] = img1
    canvas[:h2, w1:w1+w2] = img2
    
    fig, ax = plt.subplots(1, 1, figsize=(16, 8))
    ax.imshow(canvas)
    
    # Use color gradient for match quality (green = best, red = worst)
    colors = plt.cm.RdYlGn_r(np.linspace(0, 0.5, len(best_matches)))
    
    for idx, ((i, j), color, dist) in enumerate(zip(best_matches, colors, best_distances)):
        y1, x1 = keypoints1[i]
        y2, x2 = keypoints2[j]
        x2_adj = x2 + w1
        
        # Plot keypoints
        ax.plot(x1, y1, 'o', color=color, markersize=10, markeredgecolor='white', markeredgewidth=2)
        ax.plot(x2_adj, y2, 'o', color=color, markersize=10, markeredgecolor='white', markeredgewidth=2)
        
        # Draw connecting line
        ax.plot([x1, x2_adj], [y1, y2], '-', color=color, linewidth=3, alpha=0.8)
        
        # Add match number and distance
        mid_x = (x1 + x2_adj) / 2
        mid_y = (y1 + y2) / 2
        ax.text(mid_x, mid_y-10, f'{idx+1}\nd={int(dist)}', ha='center', va='center',
                bbox=dict(boxstyle='round,pad=0.3', facecolor='white', alpha=0.8),
                fontsize=8, fontweight='bold')
    
    ax.set_title(f'Top {top_n} Best Quality Matches (by Hamming Distance)', fontsize=14, fontweight='bold')
    ax.axis('off')
    
    # Add image labels
    ax.text(w1//2, -20, 'Mosaic Image', ha='center', fontsize=12, fontweight='bold')
    ax.text(w1 + w2//2, -20, 'Key Image', ha='center', fontsize=12, fontweight='bold')
    
    plt.tight_layout()
    plt.show()

# Show best quality matches
print("Best Quality Matches (Lowest Hamming Distance):")
show_best_matches(mosaic_rgb_rs, key_rgb, keypoints1, keypoints2, matches, distances, top_n=10)