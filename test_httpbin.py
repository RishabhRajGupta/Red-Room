#!/usr/bin/env python3
"""Test scanner on HTTPBin - a safe, legal testing site."""

import asyncio
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from redroom.agents.scanner.web_scanner import WebScanner

async def main():
    print("=" * 80)
    print("Testing The Red Room Scanner on HTTPBin.org")
    print("This is a LEGAL testing site designed for HTTP testing")
    print("=" * 80)
    print()
    
    url = "https://httpbin.org"
    print(f"Target: {url}")
    print("Starting scan with 70 vulnerability tests...")
    print()
    
    scanner = WebScanner(url, timeout=10)
    results = await scanner.scan()
    
    # Generate and save report
    report = scanner.generate_report()
    
    filename = "httpbin-test-report.txt"
    with open(filename, 'w', encoding='utf-8') as f:
        f.write(report)
    
    print(report)
    print()
    print(f"Report saved to: {filename}")
    print()
    print("=" * 80)
    print("SUMMARY")
    print("=" * 80)
    print(f"Endpoints Discovered: {results['endpoints_found']}")
    print(f"Vulnerabilities Found: {results['vulnerabilities_found']}")
    print(f"Tests Performed: 70")
    print()
    
    if results['vulnerabilities_found'] > 0:
        critical = len([v for v in results['vulnerabilities'] if v['severity'] == 'CRITICAL'])
        high = len([v for v in results['vulnerabilities'] if v['severity'] == 'HIGH'])
        medium = len([v for v in results['vulnerabilities'] if v['severity'] == 'MEDIUM'])
        low = len([v for v in results['vulnerabilities'] if v['severity'] == 'LOW'])
        
        print(f"CRITICAL: {critical}")
        print(f"HIGH: {high}")
        print(f"MEDIUM: {medium}")
        print(f"LOW: {low}")
    else:
        print("✓ No vulnerabilities found (HTTPBin is a well-secured test site)")
    
    print("=" * 80)

if __name__ == "__main__":
    asyncio.run(main())
