from urllib.parse import urlencode, quote
import json

def generate_report_link(image_url, image_hash=None):
    """
    Generate a pre-filled Google Images removal request link
    User will click this and complete the form on Google's site
    
    Args:
        image_url: URL of the image to report
        image_hash: SHA256 hash of the image (optional)
    
    Returns:
        URL string that user can click to report the image
    """
    try:
        # Google's removal request form
        google_report_base = "https://www.google.com/webmasters/tools/url-removal"
        
        # Pre-fill parameters
        params = {
            'url': image_url,
        }
        
        # Build the link
        report_link = f"{google_report_base}?{urlencode(params)}"
        
        return report_link
    
    except Exception as e:
        print(f"[Report] Error generating report link: {e}")
        return None

def generate_removal_email_body(image_url, image_hash, user_email=""):
    """
    Generate email text for user to send to website owner
    requesting image removal (GDPR/privacy based)
    
    Args:
        image_url: URL of the image
        image_hash: SHA256 hash of the image
        user_email: User's email address (optional)
    
    Returns:
        String with email template ready to copy/paste
    """
    
    email_body = f"""
Hello,

I am writing to request the removal of an image from your website.

IMAGE DETAILS:
- URL: {image_url}
- Hash: {image_hash}

REASON FOR REMOVAL:
This image contains my photograph without my consent and violates my privacy rights. 
As per GDPR regulations and privacy laws, I have the right to request removal of 
personal images from the internet.

I kindly request that you remove this image within 7 days.

Thank you for your cooperation.

Best regards,
{user_email if user_email else '[Your Name]'}
"""
    
    return email_body.strip()

def generate_dmca_takedown_template(image_url, copyright_holder="", contact_email=""):
    """
    Generate a DMCA takedown notice template
    User can customize and send if they own the image
    
    Args:
        image_url: URL of the image
        copyright_holder: Name of copyright holder
        contact_email: Contact email for the notice
    
    Returns:
        String with DMCA template
    """
    
    dmca_template = f"""
DIGITAL MILLENNIUM COPYRIGHT ACT (DMCA) TAKEDOWN NOTICE

To: Website Owner/Administrator
To: Hosting Provider

NOTICE OF INFRINGING MATERIAL

Pursuant to the Digital Millennium Copyright Act (DMCA), I am writing to notify you 
of infringing material on your website:

1. IDENTIFICATION OF COPYRIGHTED WORK:
   [Describe the original work, e.g., "Original photograph of myself"]

2. IDENTIFICATION OF INFRINGING MATERIAL:
   - URL: {image_url}
   - Description: [Photo of myself without permission]

3. STATEMENT UNDER PENALTY OF PERJURY:
   I have a good faith belief that use of the material is not authorized by the 
   copyright owner, its agent, or the law.

4. CONTACT INFORMATION:
   Name: {copyright_holder}
   Email: {contact_email}
   Address: [Your Address]

5. SIGNATURE:
   [Your Signature]

Please remove this content immediately.

Regards,
{copyright_holder}
"""
    
    return dmca_template.strip()

def generate_google_images_removal_link_v2(image_url):
    """
    Alternative: Direct link to Google's outdated content removal tool
    
    Args:
        image_url: URL of the image to report
    
    Returns:
        URL string for Google's removal form
    """
    try:
        # This is Google's actual removal form
        base_url = "https://www.google.com/webmasters/tools/removals"
        
        # URL encode the image URL
        encoded_url = quote(image_url, safe='')
        
        removal_link = f"{base_url}?pli=1&url={encoded_url}"
        
        return removal_link
    
    except Exception as e:
        print(f"[Report] Error generating Google removal link: {e}")
        return None

def create_removal_action_plan(image_url, image_hash):
    """
    Generate a structured action plan for user
    Shows them multiple ways to get image removed
    
    Args:
        image_url: URL of the image
        image_hash: SHA256 hash of the image
    
    Returns:
        Dictionary with step-by-step action plan
    """
    
    action_plan = {
        'priority': 'high',
        'steps': [
            {
                'step': 1,
                'action': 'Google Images Removal',
                'description': 'File a removal request with Google directly',
                'link': generate_google_images_removal_link_v2(image_url),
                'time': '1-3 days',
                'effectiveness': 'High'
            },
            {
                'step': 2,
                'action': 'Contact Website Owner',
                'description': 'Email the website to request manual removal',
                'email_template': generate_removal_email_body(image_url, image_hash),
                'time': '3-7 days',
                'effectiveness': 'Medium'
            },
            {
                'step': 3,
                'action': 'GDPR/Privacy Request',
                'description': 'File a formal privacy removal request (EU residents)',
                'template': generate_removal_email_body(image_url, image_hash),
                'time': '7-30 days',
                'effectiveness': 'High'
            }
        ],
        'additional_resources': [
            'https://support.google.com/legal/answer/3110420',
            'https://www.eff.org/deeplinks/2018/02/how-remove-your-image-internet',
        ]
    }
    
    return action_plan