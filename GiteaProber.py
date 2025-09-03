import requests
import json
import argparse
from time import time

# Globals set via CLI args
BASE_URL = None
TOKEN = None
DO_WRITE_CHECKS = False
headers = {}

# ---------------- Utility functions ----------------
def show(name, r):
    try:
        detail = r.json()
    except Exception:
        detail = r.text[:200]
    print(f"{name:40} -> {r.request.method} {r.status_code}")

def get(path, name):
    try:
        r = requests.get(f"{BASE_URL}{path}", headers=headers)
        show(name, r)
        return r
    except Exception as e:
        print(f"{name:40} -> ERROR {e}")

def post(path, name, payload):
    try:
        r = requests.post(f"{BASE_URL}{path}",
                          headers={**headers, "Content-Type":"application/json"},
                          json=payload)
        show(name, r)
        return r
    except Exception as e:
        print(f"{name:40} -> ERROR {e}")

def put(path, name, payload):
    try:
        r = requests.put(f"{BASE_URL}{path}",
                         headers={**headers, "Content-Type":"application/json"},
                         json=payload)
        show(name, r)
        return r
    except Exception as e:
        print(f"{name:40} -> ERROR {e}")

def delete(path, name):
    try:
        r = requests.delete(f"{BASE_URL}{path}", headers=headers)
        show(name, r)
        return r
    except Exception as e:
        print(f"{name:40} -> ERROR {e}")

def list_repos(endpoint, label):
    print(f"\n=== {label} ===")
    page = 1
    total_repos = 0

    while True:
        url = f"{BASE_URL}{endpoint}?page={page}&limit=50"
        try:
            r = requests.get(url, headers=headers)
            if r.status_code != 200:
                print(f"[!] {label}: HTTP {r.status_code} -> {r.text}")
                break

            repos = r.json()
            if not repos:
                break

            for repo in repos:
                total_repos += 1
                privacy = "PRIVATE" if repo['private'] else "PUBLIC"
                fork_status = "FORK" if repo['fork'] else "ORIG"
                print(f"\n - {repo['full_name']} [{privacy}] [{fork_status}]")
                if repo.get("description"):
                    print(f"  Description: {repo['description']} \n")
                if repo.get("clone_url"):
                    print(f"  Clone URL: {repo['clone_url']} \n")
            page += 1

        except Exception as e:
            print(f"[!] Error fetching {label} page {page}: {e}")
            break

    print(f"Total repositories found: {total_repos}")

# ---------------- Main ----------------
def main():
    global BASE_URL, TOKEN, headers, DO_WRITE_CHECKS

    parser = argparse.ArgumentParser(description="Gitea API CTF Testing Suite")
    parser.add_argument("--url", required=True, help="Base URL of the Gitea server (e.g. http://10.129.234.64:3000)")
    parser.add_argument("--token", required=True, help="Personal access token")
    parser.add_argument("--write", action="store_true", help="Enable write operation tests")
    args = parser.parse_args()

    BASE_URL = args.url.rstrip("/") + "/api/v1"
    TOKEN = args.token
    headers = {"Authorization": f"token {TOKEN}"}
    DO_WRITE_CHECKS = args.write

    print("="*60)
    print("GITEA API CTF TESTING SUITE")
    print("="*60)

    # Repo enumeration
    print("\n" + "="*50)
    print("DETAILED REPOSITORY ENUMERATION")
    print("="*50)
    list_repos("/user/repos", "Repositories I can access")
    list_repos("/user/starred", "Repositories I starred")
    list_repos("/admin/repos", "ALL repositories (admin scope required)")

    # Scope tests
    print("\n" + "="*50)
    print("API SCOPE AND PERMISSION TESTING")
    print("="*50)
    user_resp = get("/user", "Current user info (read:user)")
    get("/user/emails", "List user emails (read:user)")
    get("/user/followers", "User followers (read:user)")
    get("/user/following", "User following (read:user)")
    get("/user/keys", "SSH keys (read:user)")
    get("/user/gpg_keys", "GPG keys (read:user)")

    print("\n=== REPOSITORY ACCESS ===")
    get("/user/repos", "List my repositories (read:repo)")
    get("/repos/search?q=gitea", "Search public repos (read:repo)")
    get("/user/subscriptions", "Watched repos (read:repo)")

    print("\n=== ORGANIZATION ACCESS ===")
    get("/user/orgs", "List my organizations (read:org)")
    get("/orgs", "Search organizations")

    print("\n=== ISSUES & PULL REQUESTS ===")
    get("/issues", "My assigned issues (read:repo)")
    get("/user/issues", "Issues created by me (read:repo)")
    get("/notifications", "Notifications (read:user)")

    print("\n=== TEAM & COLLABORATION ===")
    get("/user/teams", "My teams (read:org)")

    print("\n=== ADMIN ENDPOINTS (requires admin scopes) ===")
    get("/admin/users", "List all users (read:admin)")
    get("/admin/orgs", "List all organizations (read:admin)")
    get("/admin/repos", "List all repositories (read:admin)")
    get("/admin/unadopted", "Unadopted repositories (read:admin)")
    get("/admin/cron", "Cron tasks (read:admin)")

    # Optional write tests
    if DO_WRITE_CHECKS:
        print("\n" + "="*50)
        print("WRITE OPERATION TESTING (ENABLED)")
        print("="*50)
        ts = str(int(time()))
        current_user = user_resp.json().get("login", "unknown") if user_resp and user_resp.status_code == 200 else "unknown"
        repo_name = f"ctf-probe-{ts}"
        create_resp = post("/user/repos", "Create test repo (write:repo)", {
            "name": repo_name,
            "private": True,
            "auto_init": True,
            "description": f"CTF API test repo - {ts}"
        })
        if create_resp and create_resp.status_code in [200, 201]:
            put(f"/repos/{current_user}/{repo_name}", "Update repo (write:repo)", {
                "description": f"Updated by CTF probe at {ts}"
            })
            post(f"/repos/{current_user}/{repo_name}/issues", "Create issue (write:repo)", {
                "title": f"Test issue {ts}", "body": "Created by CTF API probe"
            })
            delete(f"/repos/{current_user}/{repo_name}", "Delete test repo (write:repo)")

        post("/admin/users", "Create test user (write:admin)", {
            "username": f"ctf-probe-{ts}",
            "email": f"ctf-probe-{ts}@example.com",
            "password": "TempCTFPass123!"
        })
        post("/orgs", "Create test org (write:org)", {
            "username": f"ctf-org-{ts}",
            "visibility": "private",
            "description": "CTF test organization"
        })
    else:
        print("\nWRITE OPERATION TESTING DISABLED (use --write to enable)")

    # Results interpretation
    print(f"\n{'='*50}")
    print("RESULTS INTERPRETATION GUIDE")
    print("="*50)
    print("""
200/201 = Success (token has permissions)
401 = Unauthorized (invalid/expired token)
403 = Forbidden (insufficient scope)
404 = Not found (resource not accessible)
422 = Validation error
500 = Server error
""")

if __name__ == "__main__":
    main()
