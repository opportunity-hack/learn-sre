import asyncio
import aiohttp
import time
import random
import argparse
from rich.console import Console
from rich.progress import Progress
from rich import print as rprint

console = Console()

async def make_request(session, url, endpoint):
    try:
        start_time = time.time()
        async with session.get(f"{url}{endpoint}") as response:
            await response.text()
            return {
                'status': response.status,
                'latency': time.time() - start_time,
                'endpoint': endpoint
            }
    except Exception as e:
        return {
            'status': 'error',
            'latency': time.time() - start_time,
            'endpoint': endpoint,
            'error': str(e)
        }

async def load_test(url, total_requests, concurrent_requests):
    endpoints = [
        '/',
        '/products/1',
        '/products/2',
        '/products/3',
        '/products/999'  # Will cause 404
    ]
    
    results = {
        'success': 0,
        'errors': 0,
        'latencies': [],
        'status_codes': {}
    }
    
    async with aiohttp.ClientSession() as session:
        with Progress() as progress:
            task = progress.add_task("[cyan]Running load test...", total=total_requests)
            
            for batch in range(0, total_requests, concurrent_requests):
                batch_size = min(concurrent_requests, total_requests - batch)
                tasks = []
                
                for _ in range(batch_size):
                    endpoint = random.choice(endpoints)
                    tasks.append(make_request(session, url, endpoint))
                
                batch_results = await asyncio.gather(*tasks)
                
                for result in batch_results:
                    if isinstance(result['status'], int):
                        results['status_codes'][result['status']] = results['status_codes'].get(result['status'], 0) + 1
                        if 200 <= result['status'] < 300:
                            results['success'] += 1
                        else:
                            results['errors'] += 1
                    else:
                        results['errors'] += 1
                    
                    results['latencies'].append(result['latency'])
                
                progress.update(task, advance=batch_size)
                await asyncio.sleep(0.1)  # Prevent overwhelming the server
    
    return results

def print_results(results, duration):
    console.print("\n[bold green]Load Test Results[/bold green]")
    console.print(f"Duration: {duration:.2f} seconds")
    console.print(f"Total Requests: {results['success'] + results['errors']}")
    console.print(f"Successful Requests: {results['success']}")
    console.print(f"Failed Requests: {results['errors']}")
    
    if results['latencies']:
        avg_latency = sum(results['latencies']) / len(results['latencies'])
        p95_latency = sorted(results['latencies'])[int(len(results['latencies']) * 0.95)]
        console.print(f"Average Latency: {avg_latency*1000:.2f}ms")
        console.print(f"95th Percentile Latency: {p95_latency*1000:.2f}ms")
    
    console.print("\nStatus Code Distribution:")
    for status, count in results['status_codes'].items():
        console.print(f"  {status}: {count}")

async def main():
    parser = argparse.ArgumentParser(description='Load Testing Tool')
    parser.add_argument('--url', default='http://localhost:8000', help='Target URL')
    parser.add_argument('--requests', type=int, default=1000, help='Total number of requests')
    parser.add_argument('--concurrent', type=int, default=10, help='Concurrent requests')
    args = parser.parse_args()

    console.print(f"[bold]Starting load test against {args.url}[/bold]")
    console.print(f"Total requests: {args.requests}")
    console.print(f"Concurrent requests: {args.concurrent}")
    
    start_time = time.time()
    results = await load_test(args.url, args.requests, args.concurrent)
    duration = time.time() - start_time
    
    print_results(results, duration)

if __name__ == "__main__":
    asyncio.run(main())