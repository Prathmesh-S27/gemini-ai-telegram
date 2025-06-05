import os
from typing import Dict, List, Optional
import re
import asyncio
import socket
import subprocess
import platform
from pyrogram.types import Message

class AdConfig:
    def __init__(self):
        self.bot_url = os.environ.get('AD_BOT_URL', 'https://t.me/Master32v_bot')
        self.web_app_url = os.environ.get('AD_WEB_APP_URL', '')
        self.ad_enabled = os.environ.get('AD_ENABLED', 'true').lower() == 'true'
        self.ad_frequency = int(os.environ.get('AD_FREQUENCY', '5'))  # Show ad every N interactions
        
        # User session storage for configuration
        self.user_sessions = {}
        
        # Deployment environment detection
        self.is_cloud_deployment = self._detect_cloud_deployment()
        
        # Network configuration
        self.host_ip = self._get_host_ip()
        self.wifi_network = self._get_wifi_network_info()
        
        # Validate Web App URL format
        self._validate_web_app_url()
    
    def _detect_cloud_deployment(self) -> bool:
        """Detect if running in a cloud deployment environment"""
        # Check for common cloud platform environment variables
        cloud_indicators = [
            'VERCEL',  # Vercel
            'HEROKU_APP_NAME',  # Heroku
            'RAILWAY_ENVIRONMENT',  # Railway
            'RENDER',  # Render
            'AWS_LAMBDA_FUNCTION_NAME',  # AWS Lambda
            'GOOGLE_CLOUD_PROJECT',  # Google Cloud
            'AZURE_FUNCTIONS_ENVIRONMENT'  # Azure Functions
        ]
        
        return any(os.environ.get(indicator) for indicator in cloud_indicators)
        
    def _validate_web_app_url(self):
        """Validate Web App URL format"""
        if self.web_app_url:
            # Basic URL validation pattern
            url_pattern = re.compile(r'^https?://(?:www\.)?[a-zA-Z0-9-]+\.[a-zA-Z]{2,}(?:/.*)?$')
            if not url_pattern.match(self.web_app_url):
                print(f"Warning: Invalid Web App URL format: {self.web_app_url}")
                print("Expected format: https://www.example.com/ or https://example.com/path")
                self.web_app_url = ''
        
    def get_ad_message(self) -> Optional[str]:
        """Generate ad message based on configuration"""
        if not self.ad_enabled:
            return None
            
        # Only show ad if we have at least one valid URL
        if not self.bot_url and not self.web_app_url:
            return None
            
        ad_text = "🤖 **Check out our other services:**\n"
        
        if self.bot_url:
            ad_text += f"📱 Bot: {self.bot_url}\n"
            
        if self.web_app_url:
            ad_text += f"🌐 Web App: {self.web_app_url}\n"
            
        return ad_text.strip()
    
    def is_web_app_configured(self) -> bool:
        """Check if Web App URL is properly configured"""
        return bool(self.web_app_url)
    
    def get_config_status(self) -> str:
        """Get current configuration status"""
        status = f"Ad Status: {'Enabled' if self.ad_enabled else 'Disabled'}\n"
        status += f"Bot URL: {self.bot_url if self.bot_url else 'Not configured'}\n"
        status += f"Web App URL: {self.web_app_url if self.web_app_url else 'Not configured (Required field)'}\n"
        status += f"Ad Frequency: Every {self.ad_frequency} interactions\n"
        return status

    def start_configuration_session(self, user_id: int):
        """Start a configuration session for a user"""
        self.user_sessions[user_id] = {
            'step': 'web_app_url',
            'bot_url': '',
            'web_app_url': ''
        }
        
    def is_in_config_session(self, user_id: int) -> bool:
        """Check if user is in a configuration session"""
        return user_id in self.user_sessions
        
    def _get_host_ip(self) -> str:
        """Get the host IP address on WiFi network"""
        if self.is_cloud_deployment:
            return "Cloud Environment"
            
        try:
            # Create a socket connection to determine local IP
            with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
                # Connect to a remote server (doesn't actually send data)
                s.connect(("8.8.8.8", 80))
                local_ip = s.getsockname()[0]
                return local_ip
        except Exception:
            try:
                # Alternative method using hostname
                hostname = socket.gethostname()
                local_ip = socket.gethostbyname(hostname)
                return local_ip
            except Exception:
                return "Unable to detect"
    
    def _get_wifi_network_info(self) -> dict:
        """Get WiFi network information"""
        network_info = {
            'ssid': 'Unknown',
            'interface': 'Unknown'
        }
        
        if self.is_cloud_deployment:
            network_info['ssid'] = 'Cloud Network'
            return network_info
            
        try:
            system = platform.system().lower()
            
            if system == 'windows':
                # Windows command to get WiFi info
                result = subprocess.run(['netsh', 'wlan', 'show', 'profiles'], 
                                      capture_output=True, text=True)
                if result.returncode == 0:
                    lines = result.stdout.split('\n')
                    for line in lines:
                        if 'All User Profile' in line:
                            ssid = line.split(':')[1].strip()
                            network_info['ssid'] = ssid
                            break
                            
            elif system == 'linux':
                # Linux command to get WiFi info
                result = subprocess.run(['iwgetid', '-r'], 
                                      capture_output=True, text=True)
                if result.returncode == 0:
                    network_info['ssid'] = result.stdout.strip()
                    
            elif system == 'darwin':  # macOS
                # macOS command to get WiFi info
                result = subprocess.run(['/System/Library/PrivateFrameworks/Apple80211.framework/Versions/Current/Resources/airport', '-I'], 
                                      capture_output=True, text=True)
                if result.returncode == 0:
                    for line in result.stdout.split('\n'):
                        if 'SSID' in line:
                            network_info['ssid'] = line.split(':')[1].strip()
                            break
                            
        except Exception as e:
            print(f"Error getting WiFi info: {e}")
            
        return network_info
    
    def get_network_status(self) -> str:
        """Get current network status and IP information"""
        if self.is_cloud_deployment:
            deployment_platform = self._get_deployment_platform()
            status = f"""
🌐 **Cloud Deployment Information:**

☁️ Platform: {deployment_platform}
🌍 Environment: Cloud/Production
🔗 Suggested Web App URL: {self._get_suggested_cloud_url()}

💡 **For Cloud Deployment:**
- Use your actual domain URL
- Example: https://yourdomain.com/
- Vercel URL: https://your-app.vercel.app/
"""
        else:
            status = f"""
🌐 **Local Network Information:**

📍 Host IP Address: {self.host_ip}
📶 WiFi Network: {self.wifi_network['ssid']}
🔗 Local Web App URL: http://{self.host_ip}:5000/

💡 **Suggested Web App URLs:**
- Local Network: http://{self.host_ip}:5000/
- Localhost: http://localhost:5000/
"""
        
        status += f"- Current Config: {self.web_app_url if self.web_app_url else 'Not configured'}"
        return status
    
    def _get_deployment_platform(self) -> str:
        """Identify the cloud deployment platform"""
        if os.environ.get('VERCEL'):
            return 'Vercel'
        elif os.environ.get('HEROKU_APP_NAME'):
            return 'Heroku'
        elif os.environ.get('RAILWAY_ENVIRONMENT'):
            return 'Railway'
        elif os.environ.get('RENDER'):
            return 'Render'
        elif os.environ.get('AWS_LAMBDA_FUNCTION_NAME'):
            return 'AWS Lambda'
        elif os.environ.get('GOOGLE_CLOUD_PROJECT'):
            return 'Google Cloud'
        elif os.environ.get('AZURE_FUNCTIONS_ENVIRONMENT'):
            return 'Azure Functions'
        else:
            return 'Unknown Cloud Platform'
    
    def _get_suggested_cloud_url(self) -> str:
        """Get suggested URL for cloud deployment"""
        if os.environ.get('VERCEL_URL'):
            return f"https://{os.environ.get('VERCEL_URL')}/"
        elif os.environ.get('HEROKU_APP_NAME'):
            return f"https://{os.environ.get('HEROKU_APP_NAME')}.herokuapp.com/"
        else:
            return "https://your-domain.com/"
    
    def suggest_web_app_url(self) -> str:
        """Suggest Web App URL based on environment"""
        if self.is_cloud_deployment:
            return self._get_suggested_cloud_url()
        elif self.host_ip and self.host_ip != "Unable to detect":
            return f"http://{self.host_ip}:5000/"
        else:
            return "http://localhost:5000/"
    
    def auto_configure_local_webapp(self) -> str:
        """Auto-configure Web App URL using environment detection"""
        suggested_url = self.suggest_web_app_url()
        self.web_app_url = suggested_url
        
        if self.is_cloud_deployment:
            platform = self._get_deployment_platform()
            return f"""
✅ **Auto-configured for Cloud Deployment:**

☁️ Platform: {platform}
🌐 Web App URL: {suggested_url}

Note: Make sure this URL matches your actual deployed domain.
For production, consider setting AD_WEB_APP_URL environment variable.
"""
        else:
            return f"""
✅ **Auto-configured Web App URL:**

🌐 Web App URL: {suggested_url}
📍 Host IP: {self.host_ip}
📶 WiFi Network: {self.wifi_network['ssid']}

This URL will work for devices on the same WiFi network.
"""

    def process_config_input(self, user_id: int, input_text: str) -> tuple[str, bool]:
        """Process user input during configuration session"""
        if user_id not in self.user_sessions:
            return "No active configuration session.", False
            
        session = self.user_sessions[user_id]
        
        if session['step'] == 'web_app_url':
            if input_text.lower() == 'auto':
                # Auto-configure using host IP
                session['web_app_url'] = self.suggest_web_app_url()
                session['step'] = 'bot_url'
                return f"✅ Auto-configured Web App URL: {session['web_app_url']}\n\n📱 Now please provide your Bot URL (e.g., https://t.me/yourbotname)\nOr type 'skip' to skip this step:", False
            elif self._is_valid_url(input_text):
                session['web_app_url'] = input_text
                session['step'] = 'bot_url'
                return "✅ Web App URL saved!\n\n📱 Now please provide your Bot URL (e.g., https://t.me/yourbotname)\nOr type 'skip' to skip this step:", False
            else:
                return "❌ Invalid URL format. Please provide a valid Web App URL (e.g., https://www.example.com/) or type 'auto' for auto-configuration:", False
                
        elif session['step'] == 'bot_url':
            if input_text.lower() == 'skip':
                session['bot_url'] = ''
            elif self._is_valid_telegram_bot_url(input_text):
                session['bot_url'] = input_text
            else:
                return "❌ Invalid Bot URL format. Please provide a valid Telegram bot URL (e.g., https://t.me/yourbotname) or type 'skip':", False
                
            # Configuration complete
            self._save_configuration(session)
            del self.user_sessions[user_id]
            
            config_summary = f"""
✅ **Configuration Complete!**

🌐 Web App URL: {session['web_app_url']}
📱 Bot URL: {session['bot_url'] if session['bot_url'] else 'Not configured'}

Your ads are now configured and will be displayed every {self.ad_frequency} interactions.
"""
            return config_summary, True
            
        return "Invalid step in configuration.", False
        
    def _is_valid_url(self, url: str) -> bool:
        """Validate general URL format"""
        url_pattern = re.compile(r'^https?://(?:www\.)?[a-zA-Z0-9-]+\.[a-zA-Z]{2,}(?:/.*)?$')
        return bool(url_pattern.match(url))
        
    def _is_valid_telegram_bot_url(self, url: str) -> bool:
        """Validate Telegram bot URL format"""
        bot_pattern = re.compile(r'^https://t\.me/[a-zA-Z0-9_]+$')
        return bool(bot_pattern.match(url))
        
    def _save_configuration(self, session: dict):
        """Save configuration (in production, this would save to database/file)"""
        if session['web_app_url']:
            self.web_app_url = session['web_app_url']
        if session['bot_url']:
            self.bot_url = session['bot_url']
            
    def cancel_configuration(self, user_id: int) -> str:
        """Cancel ongoing configuration session"""
        if user_id in self.user_sessions:
            del self.user_sessions[user_id]
            return "❌ Configuration cancelled."
        return "No active configuration session to cancel."

# Global ad config instance
ad_config = AdConfig()

# Counter for ad frequency
interaction_counter = 0

def should_show_ad() -> bool:
    """Check if ad should be shown based on frequency"""
    global interaction_counter
    interaction_counter += 1
    
    if ad_config.ad_enabled and interaction_counter % ad_config.ad_frequency == 0:
        return True
    return False

def get_setup_instructions() -> str:
    """Get setup instructions for ad configuration"""
    instructions = """
🔧 **Ad Configuration Setup:**

Set these environment variables:

1. **AD_BOT_URL** (optional): Your Telegram bot URL
   Example: https://t.me/Master32v_bot

2. **AD_WEB_APP_URL** (required): Your web application URL
   Example: https://www.example.com/
   Format: Must start with http:// or https://

3. **AD_ENABLED** (optional): Enable/disable ads
   Values: true or false (default: true)

4. **AD_FREQUENCY** (optional): Show ad every N interactions
   Values: Any positive integer (default: 5)

Example setup:
```
export AD_BOT_URL="https://t.me/Master32v_bot"
export AD_WEB_APP_URL="https://www.example.com/"
export AD_ENABLED="true"
export AD_FREQUENCY="5"
```
"""
    return instructions

async def handle_config_command(client, message: Message):
    """Handle the /config command to start ad configuration"""
    user_id = message.from_user.id
    
    if ad_config.is_in_config_session(user_id):
        await message.reply_text("You already have an active configuration session. Type /cancelconfig to cancel it first.")
        return
        
    ad_config.start_configuration_session(user_id)
    
    network_info = ad_config.get_network_status()
    
    config_msg = f"""
🔧 **Ad Configuration Setup**

{network_info}

🌐 **Step 1: Web App URL (Required)**
Please provide your Web App URL in this format:
- https://www.example.com/
- https://example.com/path
- Type 'auto' to use local network IP: {ad_config.suggest_web_app_url()}

Type your Web App URL now or 'auto':
"""
    
    await message.reply_text(config_msg)

async def handle_config_input(client, message: Message):
    """Handle user input during configuration"""
    user_id = message.from_user.id
    
    if not ad_config.is_in_config_session(user_id):
        return False  # Not in config session
        
    response, is_complete = ad_config.process_config_input(user_id, message.text)
    await message.reply_text(response)
    
    return True  # Handled as config input

async def handle_cancel_config(client, message: Message):
    """Handle the /cancelconfig command"""
    user_id = message.from_user.id
    response = ad_config.cancel_configuration(user_id)
    await message.reply_text(response)

async def handle_network_info(client, message: Message):
    """Handle the /network command to show network information"""
    network_status = ad_config.get_network_status()
    await message.reply_text(network_status)

async def handle_auto_config(client, message: Message):
    """Handle the /autoconfig command to auto-configure using host IP"""
    result = ad_config.auto_configure_local_webapp()
    await message.reply_text(result)
