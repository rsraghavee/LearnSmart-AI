"""
Burnout Risk Dataset Generator
Creates a sample dataset for training the burnout risk prediction model.

This script generates synthetic data based on research-backed patterns:
- High study hours + low sleep = High burnout risk
- Low study hours + good sleep = Low burnout risk
- Excessive screen time = Higher burnout risk
- Insufficient breaks = Higher burnout risk
- Mood correlates with burnout risk
"""

import pandas as pd
import numpy as np
import random

def generate_burnout_dataset(num_samples=500):
    """
    Generate synthetic dataset for burnout risk prediction.
    
    Features:
    - study_hours: Hours spent studying (0-12)
    - sleep_hours: Hours of sleep (4-12)
    - break_time: Hours of break/rest (0-6)
    - screen_time: Total screen time (2-14)
    - mood_score: Numeric mood score (1-10, where 1=Low, 5=Medium, 10=High)
    
    Target:
    - burnout_risk: Low, Medium, High
    """
    
    data = []
    random.seed(42)  # For reproducibility
    np.random.seed(42)
    
    for _ in range(num_samples):
        # Generate features with some correlation to burnout risk
        study_hours = round(random.uniform(2, 12), 1)
        sleep_hours = round(random.uniform(4, 11), 1)
        break_time = round(random.uniform(0, 5), 1)
        screen_time = round(random.uniform(2, 14), 1)
        
        # Calculate burnout risk based on patterns
        # High burnout indicators:
        # - Study > 8 hours
        # - Sleep < 6 hours
        # - Break < 1 hour
        # - Screen time > 10 hours
        # - Low mood
        
        burnout_score = 0
        
        # Study hours contribution
        if study_hours > 8:
            burnout_score += 2
        elif study_hours > 6:
            burnout_score += 1
        elif study_hours < 3:
            burnout_score += 1  # Too little can also indicate issues
        
        # Sleep hours contribution
        if sleep_hours < 6:
            burnout_score += 3
        elif sleep_hours < 7:
            burnout_score += 2
        elif sleep_hours > 10:
            burnout_score += 1  # Oversleeping can indicate fatigue
        
        # Break time contribution
        if break_time < 0.5:
            burnout_score += 2
        elif break_time < 1:
            burnout_score += 1
        elif break_time > 4:
            burnout_score += 1  # Too much break can indicate avoidance
        
        # Screen time contribution
        if screen_time > 10:
            burnout_score += 2
        elif screen_time > 8:
            burnout_score += 1
        
        # Generate mood score (inversely related to burnout)
        # Higher burnout = lower mood
        if burnout_score >= 6:
            mood_score = random.randint(1, 4)  # Low mood
        elif burnout_score >= 4:
            mood_score = random.randint(3, 6)  # Medium mood
        else:
            mood_score = random.randint(5, 10)  # Higher mood
        
        # Add some randomness to mood
        mood_score = max(1, min(10, mood_score + random.randint(-1, 1)))
        
        # Determine burnout risk category
        if burnout_score >= 7:
            burnout_risk = "High"
        elif burnout_score >= 4:
            burnout_risk = "Medium"
        else:
            burnout_risk = "Low"
        
        # Add some noise - occasionally flip the label based on mood
        if mood_score <= 2 and burnout_risk == "Low":
            burnout_risk = "Medium"
        elif mood_score >= 9 and burnout_risk == "High":
            burnout_risk = "Medium"
        
        data.append({
            'study_hours': study_hours,
            'sleep_hours': sleep_hours,
            'break_time': break_time,
            'screen_time': screen_time,
            'mood_score': mood_score,
            'burnout_risk': burnout_risk
        })
    
    # Create DataFrame
    df = pd.DataFrame(data)
    
    # Shuffle the dataset
    df = df.sample(frac=1, random_state=42).reset_index(drop=True)
    
    return df


if __name__ == "__main__":
    print("Generating burnout risk dataset...")
    df = generate_burnout_dataset(num_samples=500)
    
    # Save to CSV
    df.to_csv('burnout_dataset.csv', index=False)
    print(f"Dataset saved to 'burnout_dataset.csv'")
    print(f"Total samples: {len(df)}")
    print(f"\nDataset Statistics:")
    print(df.describe())
    print(f"\nBurnout Risk Distribution:")
    print(df['burnout_risk'].value_counts())
    print(f"\nFirst 10 rows:")
    print(df.head(10))

