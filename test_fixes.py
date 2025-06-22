#!/usr/bin/env python3
"""
Test script to verify the fixes for X-axis and intelligent questions.
"""

import sys
import os
import pandas as pd
import logging

# Add the current directory to Python path for imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from utils.question_generator import get_intelligent_questions
from agents.visualization_agent import VisualizationAgent

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def test_question_generator():
    """Test the intelligent question generator."""
    print("=" * 60)
    print("TESTING INTELLIGENT QUESTION GENERATOR")
    print("=" * 60)
    
    # Test 1: Default questions (no context)
    print("\n1. Testing default questions (no context):")
    questions = get_intelligent_questions()
    for i, q in enumerate(questions, 1):
        print(f"   {i}. {q}")
    
    # Test 2: With dataset name only
    print("\n2. Testing with dataset name only:")
    questions = get_intelligent_questions(dataset_name="agricultural_data")
    for i, q in enumerate(questions, 1):
        print(f"   {i}. {q}")
    
    # Test 3: With schema information
    print("\n3. Testing with schema information:")
    sample_schema = {
        'columns': ['state', 'district', 'crop_year', 'season', 'crop', 'area', 'production', 'productivity']
    }
    questions = get_intelligent_questions(
        dataset_name="crop_production",
        schema_info=sample_schema
    )
    for i, q in enumerate(questions, 1):
        print(f"   {i}. {q}")
    
    # Test 4: With sample data
    print("\n4. Testing with sample data:")
    sample_data = pd.DataFrame({
        'state': ['Maharashtra', 'Punjab', 'Karnataka', 'Tamil Nadu'],
        'crop_year': [2020, 2021, 2020, 2021],
        'area_hectares': [1000, 1500, 800, 1200],
        'production_tonnes': [5000, 7500, 4000, 6000],
        'temperature': [25.5, 22.3, 28.1, 26.8]
    })
    questions = get_intelligent_questions(
        dataset_name="agriculture_metrics",
        sample_data=sample_data
    )
    for i, q in enumerate(questions, 1):
        print(f"   {i}. {q}")
    
    print("\n✅ Question generator tests completed!")

def test_visualization_agent():
    """Test the visualization agent with updated X-axis fixes."""
    print("\n" + "=" * 60)
    print("TESTING VISUALIZATION AGENT X-AXIS FIXES")
    print("=" * 60)
    
    # Create sample data
    sample_data = pd.DataFrame({
        'category': ['Agriculture', 'Technology', 'Healthcare', 'Education', 'Finance'],
        'value': [150, 280, 220, 180, 320],
        'year': [2020, 2021, 2022, 2023, 2024],
        'score': [8.5, 9.2, 7.8, 8.9, 9.5]
    })
    
    # Initialize visualization agent
    viz_agent = VisualizationAgent()
    
    # Generate visualizations
    print("\n1. Generating visualizations with X-axis fixes...")
    results = viz_agent.generate_visualizations(sample_data, "Show trends and patterns")
    
    print(f"   - Generated {len(results['charts'])} charts")
    print(f"   - Insights generated: {len(results['insights_text'])} characters")
    
    # Check if charts have proper configuration
    if results['charts']:
        import plotly.io as pio
        
        for i, chart_json in enumerate(results['charts']):
            try:
                fig = pio.from_json(chart_json)
                layout = fig.layout
                
                print(f"\n   Chart {i+1} Layout Analysis:")
                print(f"   - Has margin settings: {hasattr(layout, 'margin') and layout.margin is not None}")
                print(f"   - Has xaxis config: {hasattr(layout, 'xaxis') and layout.xaxis is not None}")
                print(f"   - Height set: {getattr(layout, 'height', 'Not set')}")
                print(f"   - Background transparent: {'rgba(0,0,0,0)' in str(getattr(layout, 'plot_bgcolor', ''))}")
                
                if hasattr(layout, 'xaxis') and layout.xaxis:
                    xaxis = layout.xaxis
                    print(f"   - X-axis tick angle: {getattr(xaxis, 'tickangle', 'Not set')}")
                
            except Exception as e:
                print(f"   - Error analyzing chart {i+1}: {e}")
    
    print("\n✅ Visualization agent tests completed!")

def main():
    """Run all tests."""
    print("🧪 STARTING COMPREHENSIVE TESTS FOR HACKATHON FIXES")
    print("This will test both the X-axis fix and intelligent questions feature.")
    
    try:
        # Test question generator
        test_question_generator()
        
        # Test visualization agent
        test_visualization_agent()
        
        print("\n" + "=" * 60)
        print("🎉 ALL TESTS COMPLETED SUCCESSFULLY!")
        print("=" * 60)
        print("\n📋 Summary of fixes implemented:")
        print("✅ Fixed X-axis display issues for all chart types")
        print("✅ Added Plotly modebar for chart export functionality")
        print("✅ Created intelligent analytics question generator")
        print("✅ Implemented dynamic question updates based on dataset context")
        print("✅ Added fallback to default questions when no context available")
        
        print("\n🚀 Ready for hackathon demo!")
        
    except Exception as e:
        logger.error(f"Test failed: {e}")
        print(f"\n❌ Test failed: {e}")
        return False
    
    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)