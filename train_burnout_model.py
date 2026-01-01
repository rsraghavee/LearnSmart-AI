"""
Burnout Risk Prediction Model Training Script

This script trains a Decision Tree classifier to predict burnout risk
based on study patterns.

Model: Decision Tree Classifier
Features: study_hours, sleep_hours, break_time, screen_time, mood_score
Target: burnout_risk (Low, Medium, High)

Why Decision Tree?
- Easy to interpret and explain
- No feature scaling required
- Handles non-linear relationships
- Good for small to medium datasets
- Visualizable decision rules
"""

import pandas as pd
import numpy as np
from sklearn.tree import DecisionTreeClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, classification_report, confusion_matrix
import joblib
import os

def load_dataset(csv_file='burnout_dataset.csv'):
    """Load the dataset from CSV file."""
    if not os.path.exists(csv_file):
        print(f"Error: {csv_file} not found!")
        print("Please run 'generate_burnout_dataset.py' first to create the dataset.")
        return None
    
    df = pd.read_csv(csv_file)
    return df


def prepare_data(df):
    """
    Prepare data for training.
    
    Converts mood_level (Low/Medium/High) to numeric mood_score if needed.
    """
    # Features
    feature_columns = ['study_hours', 'sleep_hours', 'break_time', 'screen_time', 'mood_score']
    X = df[feature_columns].values
    
    # Target (convert to numeric for easier handling)
    y = df['burnout_risk'].values
    
    return X, y, feature_columns


def train_model(X, y, model_type='decision_tree'):
    """
    Train machine learning classifier for burnout risk prediction.
    
    Supports two algorithms:
    1. Decision Tree: Easy to interpret, no feature scaling needed
    2. Logistic Regression: Probabilistic, good for binary-like problems
    
    Args:
        X: Feature matrix
        y: Target labels
        model_type: 'decision_tree' or 'logistic_regression'
    
    Returns:
        Trained model, test data, and predictions
    """
    # Split data into training and testing sets (80-20 split)
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42, stratify=y
    )
    
    # Choose model based on type
    if model_type == 'logistic_regression':
        # Logistic Regression for multi-class classification
        clf = LogisticRegression(
            max_iter=1000,        # Maximum iterations
            random_state=42,      # For reproducibility
            multi_class='multinomial',  # For multi-class (Low/Medium/High)
            solver='lbfgs'        # Good solver for small datasets
        )
        print("Training Logistic Regression classifier...")
    else:
        # Decision Tree classifier (default)
        clf = DecisionTreeClassifier(
            max_depth=5,              # Limit depth to prevent overfitting
            min_samples_split=10,     # Require at least 10 samples to split
            min_samples_leaf=5,       # Require at least 5 samples in leaf
            random_state=42,          # For reproducibility
            criterion='gini'          # Gini impurity for splitting
        )
        print("Training Decision Tree classifier...")
    
    # Train the model
    clf.fit(X_train, y_train)
    
    # Evaluate on training set
    y_train_pred = clf.predict(X_train)
    train_accuracy = accuracy_score(y_train, y_train_pred)
    
    # Evaluate on test set
    y_test_pred = clf.predict(X_test)
    test_accuracy = accuracy_score(y_test, y_test_pred)
    
    print(f"\nModel Performance ({model_type.upper()}):")
    print(f"Training Accuracy: {train_accuracy:.4f} ({train_accuracy*100:.2f}%)")
    print(f"Test Accuracy: {test_accuracy:.4f} ({test_accuracy*100:.2f}%)")
    
    print(f"\nClassification Report (Test Set):")
    print(classification_report(y_test, y_test_pred))
    
    print(f"\nConfusion Matrix (Test Set):")
    print(confusion_matrix(y_test, y_test_pred))
    
    return clf, X_test, y_test, y_test_pred


def save_model(model, filename='burnout_model.pkl', model_type='decision_tree'):
    """Save the trained model to a file."""
    joblib.dump(model, filename)
    print(f"\n{model_type.upper()} model saved to '{filename}'")


def load_model(filename='burnout_model.pkl'):
    """Load a saved model from file."""
    if not os.path.exists(filename):
        return None
    return joblib.load(filename)


if __name__ == "__main__":
    print("=" * 60)
    print("Burnout Risk Prediction Model Training")
    print("=" * 60)
    
    # Load dataset
    print("\n1. Loading dataset...")
    df = load_dataset()
    if df is None:
        exit(1)
    
    print(f"Dataset loaded: {len(df)} samples")
    print(f"Features: {list(df.columns[:-1])}")
    print(f"Target: {df.columns[-1]}")
    print(f"\nTarget distribution:")
    print(df['burnout_risk'].value_counts())
    
    # Prepare data
    print("\n2. Preparing data...")
    X, y, feature_names = prepare_data(df)
    print(f"Features shape: {X.shape}")
    print(f"Target shape: {y.shape}")
    
    # Train model (default: Decision Tree, can change to 'logistic_regression')
    print("\n3. Training model...")
    model_type = 'decision_tree'  # Change to 'logistic_regression' to use Logistic Regression
    model, X_test, y_test, y_test_pred = train_model(X, y, model_type=model_type)
    
    # Save model
    print("\n4. Saving model...")
    save_model(model, model_type=model_type)
    
    # Test prediction on a few examples
    print("\n5. Testing predictions on sample data:")
    print("-" * 60)
    sample_data = [
        [8.0, 5.0, 0.5, 12.0, 2],  # High burnout: high study, low sleep, low break, high screen, low mood
        [4.0, 8.0, 2.0, 6.0, 8],   # Low burnout: moderate study, good sleep, good break, moderate screen, high mood
        [6.0, 6.5, 1.5, 8.0, 5],   # Medium burnout: moderate values
    ]
    
    for i, sample in enumerate(sample_data):
        prediction = model.predict([sample])[0]
        probabilities = model.predict_proba([sample])[0]
        print(f"\nSample {i+1}: {dict(zip(feature_names, sample))}")
        print(f"Prediction: {prediction}")
        print(f"Probabilities: {dict(zip(model.classes_, probabilities))}")
    
    print("\n" + "=" * 60)
    print("Training complete!")
    print("=" * 60)

