#!/usr/bin/env python3
"""
INSTAGRAM ULTIMATE SNIPER v5.0 - TERMINAL EDITION
4 Letter Username Hunter - 10K Generator + Advanced Features
"""

import os
import sys
import time
import json
import random
import string
import threading
import requests
import signal
from datetime import datetime
from queue import Queue
from collections import deque
import itertools

# Colors Configuration
COLORS = {
    'black': '\033[30m',
    'red': '\033[31m',
    'green': '\033[32m',
    'yellow': '\033[33m',
    'blue': '\033[34m',
    'magenta': '\033[35m',
    'cyan': '\033[36m',
    'white': '\033[37m',
    'bg_red': '\033[41m',
    'bg_green': '\033[42m',
    'bg_yellow': '\033[43m',
    'bg_blue': '\033[44m',
    'bold': '\033[1m',
    'underline': '\033[4m',
    'blink': '\033[5m',
    'reverse': '\033[7m',
    'reset': '\033[0m'
}

# Emoji indicators
EMOJI = {
    'rocket': '🚀',
    'fire': '🔥',
    'skull': '💀',
    'check': '✅',
    'cross': '❌',
    'warning': '⚠️',
    'proxy': '🌐',
    'target': '🎯',
    'trophy': '🏆',
    'stop': '🛑',
    'fast': '⚡',
    'money': '💰',
    'lock': '🔒',
    'unlock': '🔓',
    'stats': '📊',
    'save': '💾',
    'time': '⏰',
    'gear': '⚙️'
}

class Config:
    """Configuration settings"""
    MAX_USERNAMES = 10000
    MAX_THREADS = 25
    PROXY_TIMEOUT = 2
    CHECK_TIMEOUT = 3
    DELAY_MIN = 0.1
    DELAY_MAX = 0.5
    SAVE_INTERVAL = 50
    STATS_INTERVAL = 2
    
class ProxyPool:
    """Advanced proxy manager with scoring"""
    
    def __init__(self):
        self.proxies = {}
        self.working = {}
        self.failed = {}
        self.lock = threading.Lock()
        self.current = 0
        self.sources = [
            {
                'url': 'https://api.proxyscrape.com/v2/?request=getproxies&protocol=http&timeout=5000&country=all',
                'type': 'http'
            },
            {
                'url': 'https://raw.githubusercontent.com/TheSpeedX/PROXY-List/master/http.txt',
                'type': 'http'
            },
            {
                'url': 'https://raw.githubusercontent.com/ShiftyTR/Proxy-List/master/http.txt',
                'type': 'http'
            },
            {
                'url': 'https://raw.githubusercontent.com/monosans/proxy-list/main/proxies/http.txt',
                'type': 'http'
            },
            {
                'url': 'https://raw.githubusercontent.com/jetkai/proxy-list/main/online-proxies/txt/proxies-http.txt',
                'type': 'http'
            },
            {
                'url': 'https://raw.githubusercontent.com/roosterkid/openproxylist/main/HTTP_RAW.txt',
                'type': 'http'
            },
            {
                'url': 'https://raw.githubusercontent.com/elliottophellia/yakumo/master/results/http.txt',
                'type': 'http'
            }
        ]
        
    def fetch_all(self):
        """Fetch proxies from all sources simultaneously"""
        print(f"{COLORS['cyan']}{EMOJI['proxy']} Fetching proxies from multiple sources...{COLORS['reset']}")
        
        def fetch_source(source):
            try:
                response = requests.get(source['url'], timeout=5)
                if response.status_code == 200:
                    proxies = response.text.strip().split('\n')
                    valid = [p.strip() for p in proxies if p.strip() and ':' in p]
                    with self.lock:
                        for proxy in valid:
                            self.proxies[proxy] = {
                                'type': source['type'],
                                'source': source['url'].split('/')[2],
                                'score': 100,
                                'speed': 0,
                                'last_used': 0,
                                'failures': 0
                            }
                    return len(valid)
            except:
                return 0
        
        threads = []
        results = []
        for source in self.sources:
            thread = threading.Thread(target=lambda s: results.append(fetch_source(s)), args=(source,))
            thread.start()
            threads.append(thread)
        
        for thread in threads:
            thread.join()
        
        total = len(self.proxies)
        print(f"{COLORS['green']}{EMOJI['check']} Fetched {total} unique proxies{COLORS['reset']}")
        return total
    
    def test_proxy_speed(self, proxy, proxy_info):
        """Test proxy with speed measurement"""
        try:
            start = time.time()
            proxy_dict = {
                'http': f'http://{proxy}',
                'https': f'http://{proxy}'
            }
            
            # Test with multiple endpoints
            test_urls = [
                'http://httpbin.org/ip',
                'http://ip-api.com/json',
                'http://ifconfig.me/ip'
            ]
            
            for url in test_urls:
                try:
                    response = requests.get(url, proxies=proxy_dict, timeout=Config.PROXY_TIMEOUT)
                    if response.status_code == 200:
                        speed = time.time() - start
                        proxy_info['speed'] = speed
                        proxy_info['last_tested'] = time.time()
                        return True, speed
                except:
                    continue
                    
        except Exception as e:
            pass
        return False, 999
    
    def test_all_fast(self, max_proxies=500):
        """Test proxies with parallel processing"""
        print(f"{COLORS['cyan']}{EMOJI['fast']} Testing proxies for speed...{COLORS['reset']}")
        
        self.working = {}
        tested = 0
        proxy_items = list(self.proxies.items())[:max_proxies]
        total = len(proxy_items)
        
        def test_worker(proxy, info):
            nonlocal tested
            success, speed = self.test_proxy_speed(proxy, info)
            with self.lock:
                tested += 1
                if success:
                    self.working[proxy] = info
                    info['working'] = True
                else:
                    info['working'] = False
                
                if tested % 50 == 0:
                    print(f"{COLORS['blue']}  Progress: {tested}/{total} - Working: {len(self.working)}{COLORS['reset']}")
        
        threads = []
        for proxy, info in proxy_items:
            thread = threading.Thread(target=test_worker, args=(proxy, info))
            thread.start()
            threads.append(thread)
            
            if len(threads) >= 100:
                for t in threads:
                    t.join()
                threads = []
        
        for thread in threads:
            thread.join()
        
        # Sort by speed
        self.working = dict(sorted(self.working.items(), key=lambda x: x[1]['speed']))
        
        print(f"{COLORS['green']}{EMOJI['check']} Found {len(self.working)} working proxies{COLORS['reset']}")
        if self.working:
            fastest = list(self.working.items())[0]
            print(f"{COLORS['green']}  Fastest: {fastest[0]} - {fastest[1]['speed']:.3f}s{COLORS['reset']}")
        
        return self.working
    
    def get_best_proxy(self):
        """Get the best working proxy based on score and speed"""
        if not self.working:
            return None
        
        with self.lock:
            # Sort by score and speed
            sorted_proxies = sorted(self.working.items(), 
                                  key=lambda x: (x[1]['score'], -x[1]['speed']), 
                                  reverse=True)
            
            for proxy, info in sorted_proxies[:10]:  # Check top 10
                if info['failures'] < 3:  # Max 3 failures
                    info['last_used'] = time.time()
                    info['score'] -= 1  # Decrease score when used
                    return proxy
            
            # If all top proxies have failures, reset some
            for proxy, info in sorted_proxies[:20]:
                info['failures'] = max(0, info['failures'] - 1)
            
            return sorted_proxies[0][0] if sorted_proxies else None
    
    def report_failure(self, proxy):
        """Report a failed proxy"""
        if proxy in self.working:
            self.working[proxy]['failures'] += 1
            self.working[proxy]['score'] -= 10
            if self.working[proxy]['failures'] >= 3:
                del self.working[proxy]
    
    def report_success(self, proxy):
        """Report a successful proxy use"""
        if proxy in self.working:
            self.working[proxy]['score'] = min(100, self.working[proxy]['score'] + 1)
            self.working[proxy]['failures'] = max(0, self.working[proxy]['failures'] - 1)

class UsernameGenerator:
    """Advanced username generator"""
    
    def __init__(self):
        self.generated = set()
        self.lock = threading.Lock()
        
        # Patterns for 4-letter usernames
        self.patterns = [
            # Common patterns
            lambda: ''.join(random.choices(string.ascii_lowercase, k=4)),
            lambda: random.choice(string.ascii_lowercase) + ''.join(random.choices(string.ascii_lowercase, k=3)),
            lambda: ''.join(random.choices(string.ascii_lowercase, k=2)) + ''.join(random.choices(string.digits, k=2)),
            lambda: ''.join(random.choices(string.ascii_lowercase, k=3)) + random.choice(string.digits),
            lambda: random.choice(string.digits) + ''.join(random.choices(string.ascii_lowercase, k=3)),
            
            # Word-like patterns
            lambda: random.choice(['x', 'z', 'q']) + ''.join(random.choices('aeiou', k=1)) + ''.join(random.choices(string.ascii_lowercase, k=2)),
            lambda: ''.join(random.choices(string.ascii_lowercase, k=2)) + random.choice(['x', 'z', 'q']) + random.choice('aeiou'),
            
            # Number patterns
            lambda: ''.join(random.choices(string.digits, k=4)),
            lambda: random.choice(string.ascii_lowercase) + ''.join(random.choices(string.digits, k=3)),
            
            # Mixed patterns
            lambda: random.choice(['_', '.']) + ''.join(random.choices(string.ascii_lowercase, k=3)),
            lambda: ''.join(random.choices(string.ascii_lowercase, k=2)) + random.choice(['_', '.']) + random.choice(string.ascii_lowercase),
        ]
        
        # Premium patterns (rare combinations)
        self.premium_patterns = [
            # CVCV pattern (Consonant-Vowel-Consonant-Vowel)
            lambda: random.choice('bcdfghjklmnpqrstvwxyz') + random.choice('aeiou') + random.choice('bcdfghjklmnpqrstvwxyz') + random.choice('aeiou'),
            
            # VCVC pattern
            lambda: random.choice('aeiou') + random.choice('bcdfghjklmnpqrstvwxyz') + random.choice('aeiou') + random.choice('bcdfghjklmnpqrstvwxyz'),
            
            # Popular letters
            lambda: random.choice('abcde') + random.choice('fghij') + random.choice('klmno') + random.choice('pqrst'),
            
            # Rare letters combo
            lambda: random.choice('xyzq') + random.choice('aeiou') + random.choice('xyzq') + random.choice('aeiou'),
        ]
    
    def generate_batch(self, count, premium_chance=0.3):
        """Generate a batch of usernames"""
        batch = set()
        
        while len(batch) < count:
            # Decide pattern type
            if random.random() < premium_chance:
                pattern = random.choice(self.premium_patterns)
            else:
                pattern = random.choice(self.patterns)
            
            username = pattern()
            
            # Validate username
            if self.is_valid(username) and username not in self.generated:
                batch.add(username)
                with self.lock:
                    self.generated.add(username)
        
        return list(batch)
    
    def is_valid(self, username):
        """Check if username is valid"""
        if len(username) != 4:
            return False
        
        # Instagram rules for 4-letter usernames
        # Can't start or end with special chars
        if username[0] in '._' or username[-1] in '._':
            return False
        
        # Can't have two special chars in a row
        for i in range(len(username)-1):
            if username[i] in '._' and username[i+1] in '._':
                return False
        
        # Must have at least one letter
        if not any(c.isalpha() for c in username):
            return False
        
        return True
    
    def generate_from_wordlist(self, wordlist_file=None):
        """Generate usernames from common words"""
        common = [
            'root', 'admin', 'user', 'test', 'love', 'live', 'free', 'game',
            'play', 'star', 'gold', 'king', 'queen', 'baby', 'cool', 'nice',
            'good', 'best', 'real', 'only', 'team', 'club', 'zone', 'area',
            'city', 'town', 'home', 'work', 'life', 'time', 'dayz', 'night',
            'week', 'month', 'year', 'blue', 'red', 'green', 'dark', 'light',
            'soft', 'hard', 'fast', 'slow', 'high', 'low', 'big', 'small',
            'hot', 'cold', 'warm', 'cool', 'new', 'old', 'young', 'old',
            'rich', 'poor', 'good', 'bad', 'true', 'false', 'open', 'close'
        ]
        return [w for w in common if len(w) == 4 and w not in self.generated]

class InstagramSniper:
    """Main sniper class with advanced features"""
    
    def __init__(self):
        self.proxy_pool = ProxyPool()
        self.generator = UsernameGenerator()
        self.usernames = []
        self.available = []
        self.checked = 0
        self.failed = 0
        self.rate_limited = 0
        self.start_time = None
        self.running = False
        self.paused = False
        self.lock = threading.Lock()
        self.stats_lock = threading.Lock()
        self.user_agents = self.load_user_agents()
        
        # Stats tracking
        self.stats = {
            'total': 0,
            'available': 0,
            'taken': 0,
            'errors': 0,
            'rate_limits': 0,
            'cpm': 0,  # Checks per minute
            'success_rate': 0
        }
        
        # For CPM calculation
        self.check_times = deque(maxlen=60)
        
    def load_user_agents(self):
        """Load user agents"""
        return [
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.0 Safari/605.1.15',
            'Mozilla/5.0 (iPhone; CPU iPhone OS 17_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.0 Mobile/15E148 Safari/604.1',
            'Mozilla/5.0 (Linux; Android 13; SM-S918B) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/112.0.0.0 Mobile Safari/537.36',
            'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/121.0',
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:109.0) Gecko/20100101 Firefox/121.0',
            'Mozilla/5.0 (iPad; CPU OS 17_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.0 Mobile/15E148 Safari/604.1'
        ]
    
    def generate_usernames(self, count, premium=True):
        """Generate usernames"""
        print(f"{COLORS['cyan']}{EMOJI['target']} Generating {count} usernames...{COLORS['reset']}")
        
        batch_size = 1000
        generated = []
        
        for i in range(0, count, batch_size):
            size = min(batch_size, count - i)
            batch = self.generator.generate_batch(size, premium_chance=0.4 if premium else 0.1)
            generated.extend(batch)
            
            progress = (i + size) / count * 100
            print(f"{COLORS['blue']}  Progress: {progress:.1f}% ({len(generated)}/{count}){COLORS['reset']}")
        
        self.usernames = generated
        print(f"{COLORS['green']}{EMOJI['check']} Generated {len(self.usernames)} usernames{COLORS['reset']}")
        return generated
    
    def load_from_file(self, filename):
        """Load usernames from file"""
        try:
            with open(filename, 'r') as f:
                self.usernames = [line.strip() for line in f if line.strip()][:Config.MAX_USERNAMES]
            print(f"{COLORS['green']}{EMOJI['check']} Loaded {len(self.usernames)} usernames from {filename}{COLORS['reset']}")
        except Exception as e:
            print(f"{COLORS['red']}{EMOJI['cross']} Error loading file: {e}{COLORS['reset']}")
    
    def save_results(self):
        """Save results to file"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"available_{timestamp}.txt"
        
        with open(filename, 'w') as f:
            for username in self.available:
                f.write(f"{username}\n")
        
        # Also save to main file
        with open('available.txt', 'w') as f:
            for username in self.available:
                f.write(f"{username}\n")
        
        print(f"{COLORS['green']}{EMOJI['save']} Saved {len(self.available)} usernames to {filename}{COLORS['reset']}")
    
    def check_username(self, username):
        """Check username with advanced detection"""
        proxy = self.proxy_pool.get_best_proxy()
        
        if not proxy:
            return "no_proxy", None
        
        try:
            proxy_dict = {
                'http': f'http://{proxy}',
                'https': f'http://{proxy}'
            }
            
            # Randomize request
            headers = {
                'User-Agent': random.choice(self.user_agents),
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
                'Accept-Language': 'en-US,en;q=0.5',
                'Accept-Encoding': 'gzip, deflate',
                'DNT': '1',
                'Connection': 'keep-alive',
                'Upgrade-Insecure-Requests': '1',
            }
            
            # Try different endpoints
            endpoints = [
                f"https://www.instagram.com/{username}/",
                f"https://instagram.com/{username}/",
                f"https://i.instagram.com/api/v1/users/web_profile_info/?username={username}"
            ]
            
            for url in endpoints:
                try:
                    response = requests.get(url, proxies=proxy_dict, headers=headers, 
                                         timeout=Config.CHECK_TIMEOUT, allow_redirects=True)
                    
                    # Analyze response
                    if response.status_code == 404:
                        self.proxy_pool.report_success(proxy)
                        return "available", proxy
                    elif response.status_code == 200:
                        # Check if it's actually available (Instagram sometimes returns 200 with "Page Not Found")
                        if 'Page Not Found' in response.text or 'This page isn\'t available' in response.text:
                            self.proxy_pool.report_success(proxy)
                            return "available", proxy
                        self.proxy_pool.report_success(proxy)
                        return "taken", proxy
                    elif response.status_code == 429:
                        self.proxy_pool.report_failure(proxy)
                        return "rate_limited", proxy
                    else:
                        continue
                        
                except:
                    continue
            
            self.proxy_pool.report_failure(proxy)
            return "error", proxy
            
        except Exception as e:
            self.proxy_pool.report_failure(proxy)
            return "error", proxy
    
    def display_live_stats(self):
        """Display live statistics"""
        os.system('clear' if os.name == 'posix' else 'cls')
        
        elapsed = time.time() - self.start_time if self.start_time else 0
        hours = int(elapsed // 3600)
        minutes = int((elapsed % 3600) // 60)
        seconds = int(elapsed % 60)
        
        # Calculate CPM
        cpm = 0
        if len(self.check_times) > 1:
            time_span = self.check_times[-1] - self.check_times[0]
            if time_span > 0:
                cpm = (len(self.check_times) / time_span) * 60
        
        # Calculate success rate
        success_rate = (self.stats['available'] / max(1, self.stats['total'])) * 100
        
        # Banner
        print(f"""{COLORS['bold']}{COLORS['cyan']}
╔══════════════════════════════════════════════════════════════════╗
║                 INSTAGRAM ULTIMATE SNIPER v5.0                   ║
║                   4 Letter Username Hunter                        ║
║                    10K Generator Edition                          ║
╚══════════════════════════════════════════════════════════════════╝{COLORS['reset']}
""")
        
        # Status
        print(f"{COLORS['white']}┌─ {'=' * 50} ┐{COLORS['reset']}")
        
        status_line = f"{COLORS['bold']}STATUS:{COLORS['reset']} "
        if self.paused:
            status_line += f"{COLORS['yellow']}PAUSED {EMOJI['stop']}{COLORS['reset']}"
        elif self.running:
            status_line += f"{COLORS['green']}RUNNING {EMOJI['rocket']}{COLORS['reset']}"
        else:
            status_line += f"{COLORS['red']}STOPPED{COLORS['reset']}"
        
        print(f"{COLORS['white']}│{COLORS['reset']} {status_line:<50} {COLORS['white']}│{COLORS['reset']}")
        print(f"{COLORS['white']}│{COLORS['reset']} {COLORS['bold']}TIME:{COLORS['reset']} {hours:02d}:{minutes:02d}:{seconds:02d} {EMOJI['time']} {COLORS['white']}│{COLORS['reset']}")
        print(f"{COLORS['white']}├─ {'=' * 50} ┤{COLORS['reset']}")
        
        # Stats
        print(f"{COLORS['white']}│{COLORS['reset']} {COLORS['bold']}PROGRESS:{COLORS['reset']} {self.stats['total']}/{len(self.usernames)} ({self.stats['total']/max(1,len(self.usernames))*100:.1f}%)")
        print(f"{COLORS['white']}│{COLORS['reset']} {COLORS['bold']}CPM:{COLORS['reset']} {cpm:.0f} checks/min {EMOJI['fast']}")
        print(f"{COLORS['white']}│{COLORS['reset']} {COLORS['bold']}SUCCESS RATE:{COLORS['reset']} {success_rate:.1f}%")
        print(f"{COLORS['white']}├─ {'=' * 50} ┤{COLORS['reset']}")
        
        # Results
        print(f"{COLORS['white']}│{COLORS['reset']} {COLORS['green']}{EMOJI['check']} AVAILABLE: {self.stats['available']}{COLORS['reset']}")
        print(f"{COLORS['white']}│{COLORS['reset']} {COLORS['red']}{EMOJI['cross']} TAKEN: {self.stats['taken']}{COLORS['reset']}")
        print(f"{COLORS['white']}│{COLORS['reset']} {COLORS['yellow']}{EMOJI['warning']} RATE LIMITED: {self.stats['rate_limits']}{COLORS['reset']}")
        print(f"{COLORS['white']}│{COLORS['reset']} {COLORS['magenta']}{EMOJI['skull']} ERRORS: {self.stats['errors']}{COLORS['reset']}")
        print(f"{COLORS['white']}├─ {'=' * 50} ┤{COLORS['reset']}")
        
        # Proxy stats
        print(f"{COLORS['white']}│{COLORS['reset']} {COLORS['bold']}PROXIES:{COLORS['reset']} {EMOJI['proxy']}")
        print(f"{COLORS['white']}│{COLORS['reset']}   Working: {len(self.proxy_pool.working)}")
        print(f"{COLORS['white']}│{COLORS['reset']}   Total: {len(self.proxy_pool.proxies)}")
        print(f"{COLORS['white']}├─ {'=' * 50} ┤{COLORS['reset']}")
        
        # Recent finds
        if self.available:
            print(f"{COLORS['white']}│{COLORS['reset']} {COLORS['bold']}{EMOJI['trophy']} RECENT FINDS:{COLORS['reset']}")
            for username in self.available[-5:]:
                print(f"{COLORS['white']}│{COLORS['reset']}   {COLORS['green']}@{username}{COLORS['reset']}")
        else:
            print(f"{COLORS['white']}│{COLORS['reset']} {COLORS['yellow']}No finds yet...{COLORS['reset']}")
        
        print(f"{COLORS['white']}└─ {'=' * 50} ┘{COLORS['reset']}")
        print(f"\n{COLORS['yellow']}Commands: [P]ause | [R]esume | [S]top | [Q]uit{COLORS['reset']}")
    
    def worker(self, queue):
        """Worker thread for checking"""
        while self.running and not queue.empty():
            if self.paused:
                time.sleep(1)
                continue
            
            try:
                username = queue.get(timeout=1)
                
                start_check = time.time()
                result, proxy = self.check_username(username)
                check_time = time.time() - start_check
                
                with self.stats_lock:
                    self.stats['total'] += 1
                    self.check_times.append(time.time())
                    
                    if result == "available":
                        self.stats['available'] += 1
                        self.available.append(username)
                        print(f"\n{COLORS['green']}{EMOJI['check']} @{username} - AVAILABLE! ({check_time:.2f}s){COLORS['reset']}")
                        
                        # Save immediately
                        with open('available.txt', 'a') as f:
                            f.write(f"{username}\n")
                    
                    elif result == "taken":
                        self.stats['taken'] += 1
                    
                    elif result == "rate_limited":
                        self.stats['rate_limits'] += 1
                        print(f"\n{COLORS['yellow']}{EMOJI['warning']} Rate limited, switching proxy...{COLORS['reset']}")
                        time.sleep(1)
                    
                    elif result == "error":
                        self.stats['errors'] += 1
                    
                    elif result == "no_proxy":
                        print(f"\n{COLORS['red']}{EMOJI['cross']} No proxies available!{COLORS['reset']}")
                        self.running = False
                        break
                
                # Auto-save periodically
                if self.stats['total'] % Config.SAVE_INTERVAL == 0:
                    self.save_results()
                
                # Small delay
                delay = random.uniform(Config.DELAY_MIN, Config.DELAY_MAX)
                time.sleep(delay)
                
            except Exception as e:
                continue
    
    def start(self):
        """Start the sniper"""
        if not self.usernames:
            print(f"{COLORS['red']}{EMOJI['cross']} No usernames loaded!{COLORS['reset']}")
            return
        
        if not self.proxy_pool.working:
            print(f"{COLORS['yellow']}{EMOJI['warning']} No working proxies!{COLORS['reset']}")
            choice = input(f"{COLORS['yellow']}Fetch and test proxies now? (y/n): {COLORS['reset']}")
            if choice.lower() == 'y':
                self.proxy_pool.fetch_all()
                self.proxy_pool.test_all_fast()
            else:
                return
        
        # Create queue
        queue = Queue()
        for username in self.usernames:
            queue.put(username)
        
        # Reset stats
        self.stats = {k: 0 for k in self.stats}
        self.available = []
        self.start_time = time.time()
        self.running = True
        self.paused = False
        
        # Load existing finds
        if os.path.exists('available.txt'):
            with open('available.txt', 'r') as f:
                self.available = [line.strip() for line in f if line.strip()]
        
        print(f"{COLORS['green']}{EMOJI['rocket']} Starting sniper with {Config.MAX_THREADS} threads{COLORS['reset']}")
        print(f"{COLORS['yellow']}Press Ctrl+C to access menu{COLORS['reset']}")
        time.sleep(2)
        
        # Start workers
        threads = []
        for _ in range(Config.MAX_THREADS):
            thread = threading.Thread(target=self.worker, args=(queue,))
            thread.start()
            threads.append(thread)
        
        # Stats display thread
        def stats_display():
            while self.running:
                self.display_live_stats()
                time.sleep(Config.STATS_INTERVAL)
        
        stats_thread = threading.Thread(target=stats_display)
        stats_thread.daemon = True
        stats_thread.start()
        
        # Wait for completion with keyboard handling
        try:
            while self.running and not queue.empty():
                time.sleep(0.1)
        except KeyboardInterrupt:
            self.menu()
        
        # Stop
        self.running = False
        
        # Wait for threads
        for thread in threads:
            thread.join()
        
        # Final stats
        self.display_live_stats()
        self.save_results()
        print(f"{COLORS['green']}{EMOJI['trophy']} Sniper finished! Found {len(self.available)} available usernames{COLORS['reset']}")
    
    def menu(self):
        """Interactive menu"""
        while True:
            print(f"\n{COLORS['cyan']}{EMOJI['gear']} SNIPER MENU{COLORS['reset']}")
            print(f"{COLORS['white']}[P] Pause/Resume")
            print(f"[S] Stop")
            print(f"[R] Restart")
            print(f"[Q] Quit{COLORS['reset']}")
            
            choice = input(f"\n{COLORS['yellow']}Choice: {COLORS['reset']}").lower()
            
            if choice == 'p':
                self.paused = not self.paused
                status = "PAUSED" if self.paused else "RESUMED"
                print(f"{COLORS['yellow']}Sniper {status}{COLORS['reset']}")
            
            elif choice == 's':
                self.running = False
                print(f"{COLORS['red']}Stopping sniper...{COLORS['reset']}")
                break
            
            elif choice == 'r':
                self.running = False
                time.sleep(1)
                self.start()
                break
            
            elif choice == 'q':
                self.running = False
                print(f"{COLORS['green']}Goodbye!{COLORS['reset']}")
                sys.exit(0)

def main():
    """Main function"""
    sniper = InstagramSniper()
    
    while True:
        os.system('clear' if os.name == 'posix' else 'cls')
        
        print(f"""{COLORS['bold']}{COLORS['cyan']}
╔══════════════════════════════════════════════════════════════════╗
║              INSTAGRAM ULTIMATE SNIPER v5.0                      ║
║                    Main Menu                                      ║
╚══════════════════════════════════════════════════════════════════╝{COLORS['reset']}
""")
        
        print(f"{COLORS['white']}[1] {EMOJI['target']} Generate 10K usernames")
        print(f"[2] {EMOJI['save']} Load usernames from file")
        print(f"[3] {EMOJI['proxy']} Fetch & test proxies")
        print(f"[4] {EMOJI['rocket']} Start sniper")
        print(f"[5] {EMOJI['stats']} View results")
        print(f"[6] {EMOJI['gear']} Settings")
        print(f"[7] {EMOJI['cross']} Exit{COLORS['reset']}")
        
        choice = input(f"\n{COLORS['yellow']}Choose option: {COLORS['reset']}")
        
        if choice == '1':
            count = min(Config.MAX_USERNAMES, 10000)
            sniper.generate_usernames(count, premium=True)
            input(f"\n{COLORS['green']}Press Enter to continue...{COLORS['reset']}")
        
        elif choice == '2':
            filename = input(f"{COLORS['yellow']}Filename: {COLORS['reset']}")
            sniper.load_from_file(filename)
            input(f"\n{COLORS['green']}Press Enter to continue...{COLORS['reset']}")
        
        elif choice == '3':
            sniper.proxy_pool.fetch_all()
            sniper.proxy_pool.test_all_fast()
            input(f"\n{COLORS['green']}Press Enter to continue...{COLORS['reset']}")
        
        elif choice == '4':
            sniper.start()
        
        elif choice == '5':
            if sniper.available:
                print(f"\n{COLORS['green']}Available Usernames:{COLORS['reset']}")
                for i, username in enumerate(sniper.available, 1):
                    print(f"{COLORS['green']}[{i}] @{username}{COLORS['reset']}")
                print(f"\n{COLORS['green']}Total: {len(sniper.available)}{COLORS['reset']}")
            else:
                print(f"\n{COLORS['yellow']}No available usernames yet{COLORS['reset']}")
            input(f"\n{COLORS['green']}Press Enter to continue...{COLORS['reset']}")
        
        elif choice == '6':
            print(f"\n{COLORS['cyan']}Settings:{COLORS['reset']}")
            print(f"Max Threads: {Config.MAX_THREADS}")
            print(f"Proxy Timeout: {Config.PROXY_TIMEOUT}s")
            print(f"Check Timeout: {Config.CHECK_TIMEOUT}s")
            print(f"Delay: {Config.DELAY_MIN}-{Config.DELAY_MAX}s")
            input(f"\n{COLORS['green']}Press Enter to continue...{COLORS['reset']}")
        
        elif choice == '7':
            print(f"{COLORS['green']}Goodbye!{COLORS['reset']}")
            break

if __name__ == "__main__":
    main()