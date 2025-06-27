#!/usr/bin/env python3
"""
Test script for the enhanced OpenAI client
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from email_crm_sync.clients.openai_client import EnhancedOpenAIProcessor
from email_crm_sync.config import config

def test_enhanced_openai():
    """Test the enhanced OpenAI processing capabilities"""
    
    # Use centralized configuration
    try:
        openai_api_key = config.openai_key
        if not openai_api_key:
            raise ValueError("OpenAI API key not found in configuration")
    except Exception as e:
        print(f"❌ Error loading configuration: {e}")
        assert False, f"Error loading configuration: {e}"
    
    # Initialize the enhanced processor
    try:
        processor = EnhancedOpenAIProcessor(openai_api_key)
        print("✅ EnhancedOpenAIProcessor initialized successfully")
    except Exception as e:
        print(f"❌ Error initializing processor: {e}")
        assert False, f"Error initializing processor: {e}"
    
    # Test email content
    test_subject = "Re: Wellington Park Development - Site Visit Scheduled"
    test_body = """Dear John,

I hope this email finds you well. I wanted to follow up on our conversation about the Wellington Park development project.

We have scheduled a site visit for next Tuesday at 2 PM. Please bring your safety gear and the updated floor plans.

The property address is 45 Wellington Park Road, Bristol BS8 2UW. 

We also need to discuss the urgent deadline for the planning permission documents - they need to be submitted by Friday.

Could you please confirm your attendance and let me know if you have any questions?

Best regards,
Sarah Thompson
ABC Property Developments Ltd
Phone: 0117 123 4567
Email: sarah@abcproperty.co.uk
"""
    
    print("\n🔍 Testing comprehensive email processing...")
    print("-" * 60)
    print(f"Subject: {test_subject}")
    print(f"Body length: {len(test_body)} characters")
    
    try:
        # Test comprehensive processing
        result = processor.process_email_comprehensive(
            subject=test_subject,
            body=test_body,
            sender_email="sarah@abcproperty.co.uk"
        )
        
        print("\n📊 Comprehensive Processing Results:")
        print("-" * 40)
        for key, value in result.items():
            if isinstance(value, list):
                print(f"{key}: {value}")
            else:
                print(f"{key}: {value}")
        
        # Test backward compatibility
        print("\n🔄 Testing backward compatibility...")
        legacy_result = processor.extract_development_info_and_summary(test_subject, test_body)
        print("\n📋 Legacy Method Results:")
        print("-" * 30)
        for key, value in legacy_result.items():
            if key == 'summary':
                print(f"{key}: {value[:100]}...")  # Truncate long summary
            else:
                print(f"{key}: {value}")
        
        # Test smart keywords
        print("\n🔑 Testing smart keyword generation...")
        keywords = processor.generate_smart_keywords(test_subject, test_body)
        print(f"Generated keywords: {keywords}")
        
        # Test semantic matching (with mock developments)
        print("\n🎯 Testing semantic matching...")
        mock_developments = [
            {
                'id': 'dev_001',
                'Deal_Name': 'Wellington Park Residential',
                'Property_Address': '45 Wellington Park Road, Bristol',
                'Contact_Name': 'John Smith',
                'Account_Name': 'ABC Property Developments'
            },
            {
                'id': 'dev_002', 
                'Deal_Name': 'Riverside Gardens',
                'Property_Address': '23 River Street, Bath',
                'Contact_Name': 'Jane Doe',
                'Account_Name': 'XYZ Construction'
            }
        ]
        
        matches = processor.semantic_match_developments(result, mock_developments)
        print(f"Found {len(matches)} potential matches:")
        for match in matches:
            print(f"  - Development {match['development_id']}: {match['confidence_score']:.2f} confidence")
            print(f"    Reasons: {match['match_reasons']}")
        
        print("\n✅ All tests completed successfully!")
        assert True
        
    except Exception as e:
        print(f"❌ Error during processing: {e}")
        import traceback
        traceback.print_exc()
        assert False, f"Error during processing: {e}"

def main():
    """Main test function"""
    print("🚀 Enhanced OpenAI Client Test")
    print("=" * 50)
    
    try:
        test_enhanced_openai()
        success = True
    except AssertionError:
        success = False
    
    if success:
        print("\n🎉 Enhanced OpenAI client is working correctly!")
        return 0
    else:
        print("\n💥 Enhanced OpenAI client test failed!")
        return 1

if __name__ == "__main__":
    sys.exit(main())
