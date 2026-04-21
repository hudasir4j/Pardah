from urllib.parse import urlencode, quote, urlsplit
import json
from datetime import datetime

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


# ---------------------------------------------------------------------------
# Wizard plan: used by the /removal-plan endpoint. Returns a structured
# per-platform action plan the frontend renders as a guided wizard.
# ---------------------------------------------------------------------------

# Per-platform takedown configuration.
#
# `kind` controls how step 2 of the wizard renders:
#   - 'platform_form'  -> show a single "open the report form" button.
#                         Social media sites don't have public takedown
#                         inboxes; the in-app form is the only path.
#   - 'email'          -> show a contact email + a friendly pre-written
#                         message that the user copies into Gmail.
#
# `contact_email` is the single best-known address. We deliberately don't
# render alternatives in the UI - it's confusing and most users only need
# one address to copy.
_PLATFORM_DEEP_LINKS = {
    'instagram': {
        'label': 'Instagram',
        'kind': 'platform_form',
        'report_form': 'https://help.instagram.com/contact/504521742987441',
        'contact_email': None,
        'guidance': (
            "Instagram only accepts takedown requests through their in-app form. "
            "Sign in first so they can tie the report to your account, then paste "
            "the post URL in the \"Link to content\" field."
        ),
    },
    'facebook': {
        'label': 'Facebook',
        'kind': 'platform_form',
        'report_form': 'https://www.facebook.com/help/contact/144059062408922',
        'contact_email': None,
        'guidance': (
            "Facebook handles photo-of-me requests through their privacy form. "
            "Sign in, paste the post URL, and pick \"It shows me or a family member.\""
        ),
    },
    'twitter': {
        'label': 'X (Twitter)',
        'kind': 'platform_form',
        'report_form': 'https://help.twitter.com/en/forms/safety-and-sensitive-content/private-information',
        'contact_email': None,
        'guidance': (
            "X removes posts that share private media without consent. Paste the "
            "tweet URL and attach a screenshot."
        ),
    },
    'linkedin': {
        'label': 'LinkedIn',
        'kind': 'platform_form',
        'report_form': 'https://www.linkedin.com/help/linkedin/ask/TS-RPRT-IMG',
        'contact_email': None,
        'guidance': (
            "LinkedIn requires you to be signed in to submit image-takedown "
            "requests. Include both the profile URL and the post URL."
        ),
    },
    'tiktok': {
        'label': 'TikTok',
        'kind': 'platform_form',
        'report_form': 'https://www.tiktok.com/legal/report/Privacy',
        'contact_email': None,
        'guidance': (
            "TikTok's Privacy form handles non-consensual footage. Paste the "
            "video URL and select \"Privacy violation.\""
        ),
    },
    'google': {
        'label': 'Google Images',
        'kind': 'platform_form',
        'report_form': 'https://support.google.com/websearch/answer/9673730',
        'contact_email': None,
        'guidance': (
            "Google removes image results that reveal personal info. Click "
            "\"Start removal request\" on the page that opens."
        ),
    },
    'generic': {
        'label': 'website',
        'kind': 'email',
        'report_form': None,
        # Filled in per-host at build time (privacy@<host>).
        'contact_email': None,
        'guidance': '',
    },
}


def _resolve_contact(platform: str, host: str) -> dict:
    """
    Resolve the best contact info for this match.

    Returns `{'email': str, 'source': str, 'page_url': Optional[str]}`.
    `source` is one of:
        'platform'  - we don't email this platform at all
        'mailto'    - found on the site's contact/about page
        'text'      - found in plain text on the site
        'hunter'    - sourced from Hunter.io (if configured)
        'guess'     - heuristic fallback `privacy@<host>`
        'none'      - host unknown
    """
    meta = _PLATFORM_DEEP_LINKS.get(platform) or _PLATFORM_DEEP_LINKS['generic']
    if meta.get('kind') == 'platform_form':
        return {'email': '', 'source': 'platform', 'page_url': None}
    if meta.get('contact_email'):
        return {'email': meta['contact_email'], 'source': 'platform', 'page_url': None}
    if not host:
        return {'email': '', 'source': 'none', 'page_url': None}

    # Real lookup. Cached per-host so repeat calls during a session are free.
    try:
        from contact_finder import find_contact
        found = find_contact(host)
    except Exception:
        found = None

    if found and found.get('email'):
        return {
            'email': found['email'],
            'source': found.get('source') or 'text',
            'page_url': found.get('page_url'),
        }
    return {'email': f'privacy@{host}', 'source': 'guess', 'page_url': None}


def _detect_platform(page_url: str, image_url: str = '') -> str:
    """Return a platform key for the URL, defaulting to 'generic'."""
    url_to_check = (page_url or image_url or '').lower()
    if 'instagram.com' in url_to_check or 'cdninstagram' in url_to_check:
        return 'instagram'
    if 'facebook.com' in url_to_check or 'fbcdn' in url_to_check or 'fbsbx' in url_to_check:
        return 'facebook'
    if 'twitter.com' in url_to_check or 'x.com' in url_to_check or 'twimg' in url_to_check:
        return 'twitter'
    if 'linkedin.com' in url_to_check or 'licdn' in url_to_check:
        return 'linkedin'
    if 'tiktok.com' in url_to_check or 'tiktokcdn' in url_to_check:
        return 'tiktok'
    if 'google.com' in url_to_check or 'googleusercontent' in url_to_check:
        return 'google'
    return 'generic'


def _host(url: str) -> str:
    try:
        return (urlsplit(url).hostname or '').replace('www.', '')
    except Exception:
        return ''


def build_removal_plan(
    image_url: str,
    page_url: str = '',
    image_hash: str = '',
    user_name: str = '',
    user_email: str = '',
) -> dict:
    """
    Build a structured takedown plan for a given match. The frontend renders
    the `steps` as a wizard and shows the copyable `templates`.
    """
    page_url = page_url or image_url
    platform = _detect_platform(page_url, image_url)
    platform_meta = _PLATFORM_DEEP_LINKS[platform]
    host = _host(page_url) or _host(image_url) or 'the source site'

    display_name = user_name.strip() or '[Your Name]'
    contact = _resolve_contact(platform, host)
    contact_email = contact['email']
    contact_source = contact['source']
    contact_page_url = contact['page_url']

    # Friendly, casual message. We deliberately do NOT include image-hash,
    # GDPR/Article 17, or "I have a good faith belief" boilerplate - small
    # site owners react badly to legalese, and a personal note about the
    # hijab is far more likely to get an actual reply.
    email_body = (
        f"Hi, hope you're doing well!\n\n"
        f"There's a photo of me on this page: {page_url}\n\n"
        f"It's an older photo and I'd really appreciate it if you could take "
        f"it down. Since it was taken, I've started wearing hijab as part of "
        f"my religious practice, and I'd prefer not to have older photos of "
        f"me without my hijab on the internet.\n\n"
        f"Thank you so much for understanding!\n\n"
        f"{display_name}"
    ).rstrip()

    email_subject = f"Could you take down a photo of me from {host}?"

    dmca_body = generate_dmca_takedown_template(
        image_url=image_url,
        copyright_holder=display_name,
        contact_email=user_email.strip() or '[Your Email]',
    )

    # Step 1 is always "open the page". Step 2 changes by platform kind:
    # social media + google get a single "open the report form" button;
    # generic websites get the contact email + the friendly message.
    step1 = {
        'step': 1,
        'title': 'Check the source page',
        'description': (
            f"Make sure this is the page hosting the photo on {host} before you "
            f"reach out."
        ),
        'primary': {'label': 'Open page', 'url': page_url},
    }

    if platform_meta['kind'] == 'platform_form':
        step2 = {
            'step': 2,
            'kind': 'platform_form',
            'title': f"Report it on {platform_meta['label']}",
            'description': platform_meta['guidance'],
            'primary': {
                'label': f"Open {platform_meta['label']} report form",
                'url': platform_meta['report_form'],
            },
        }
    else:
        if contact_source in ('mailto', 'text', 'hunter'):
            step2_desc = (
                f"We found this contact address on the site itself. Copy the "
                f"email and the message into Gmail (or whatever mail app you "
                f"use) and send it."
            )
        else:
            step2_desc = (
                f"We couldn't find a contact email published on {host}, so this "
                f"is a best-guess address most sites use. If it bounces, try "
                f"the site's contact page directly."
            )
        step2 = {
            'step': 2,
            'kind': 'email',
            'title': 'Reach out to the site owner',
            'description': step2_desc,
            'contact_email': contact_email,
            'contact_source': contact_source,
            'contact_page_url': contact_page_url,
            'subject': email_subject,
            'template': email_body,
        }

    # Escalation is shown in the UI as a collapsed "Worst case" section so
    # we don't overwhelm the user with legal text up front.
    escalation = {
        'title': 'No response after a few weeks?',
        'description': (
            "If the site owner hasn't replied after two or three weeks, you can "
            "send the formal takedown notice below. This is the language hosting "
            "providers are required to act on."
        ),
        'contact_email': contact_email,
        'subject': f"DMCA takedown notice - {host}",
        'template': dmca_body,
    }

    return {
        'platform': platform,
        'platform_label': platform_meta['label'],
        'host': host,
        'page_url': page_url,
        'image_url': image_url,
        'image_hash': image_hash or None,
        'contact_email': contact_email,
        'contact_source': contact_source,
        'contact_page_url': contact_page_url,
        'steps': [step1, step2],
        'escalation': escalation,
        'templates': {
            'email': email_body,
            'email_subject': email_subject,
            'dmca': dmca_body,
        },
    }