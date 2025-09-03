
# GiteaProber.py

`GiteaProber.py` is a Python script designed for **CTF environments** or **security research labs** to probe a [Gitea](https://gitea.io) instance using an access token.  
It automates **enumeration of repositories, users, orgs, issues, and admin endpoints**, and can optionally attempt **write operations** such as creating/deleting repositories, issues, users, and organizations.  

⚠️ **Warning:**  
When write mode is enabled, this script will create and delete resources.  
Only run against systems you own or have explicit permission to test.  

---

## Features

- ✅ **Repository enumeration** (`/user/repos`, `/user/starred`, `/admin/repos`)  
- ✅ **Scope testing** (`/user`, `/orgs`, `/issues`, `/notifications`, etc.)  
- ✅ **Admin endpoints** (`/admin/users`, `/admin/orgs`, `/admin/repos`, `/admin/unadopted`, `/admin/cron`)  
- ✅ **Optional write testing** (with `--write`)  
  - Create, update, delete repositories  
  - Create issues  
  - Create users (requires `write:admin`)  
  - Create organizations  

---

## Installation

Clone the repo and install dependencies:

```bash
git clone https://github.com/yourusername/GiteaProber.git
cd GiteaProber
pip install -r requirements.txt
````

**Requirements:**

* Python 3.7+
* `requests`

Or install manually:

```bash
pip install requests
```

---

## Usage

Run the script with a Gitea server URL and personal access token.
The script automatically appends `/api/v1` to the provided base URL.

### Read-only enumeration

```bash
python3 GiteaProber.py --url http://10.129.234.64:3000 --token <YOUR_TOKEN>
```

### Enable write testing

```bash
python3 GiteaProber.py --url http://10.129.234.64:3000 --token <YOUR_TOKEN> --write
```

This will attempt creating/updating/deleting repos, issues, users, and organizations.

---

## Example Output

```text
============================================================
GITEA API CTF TESTING SUITE
============================================================

==================================================
DETAILED REPOSITORY ENUMERATION
==================================================
=== Repositories I can access ===
- bloodstiller/dev-scripts [PRIVATE] [ORIG]
  Description: CTF helper repo
  Clone URL: http://10.129.234.64:3000/bloodstiller/dev-scripts.git
Total repositories found: 1

Current user info (read:user)        -> GET 200
List user emails (read:user)         -> GET 200
User followers (read:user)           -> GET 200
```

---

## Results Interpretation

* **200 / 201** → Success (token has permissions)
* **401** → Unauthorized (invalid/expired token)
* **403** → Forbidden (insufficient scope)
* **404** → Not found (resource/endpoint not accessible)
* **422** → Validation error (bad payload)
* **500** → Server error

**CTF Scenarios:**

* Many `200`s → High privilege token (good for lateral movement)
* `403` on `/admin/*` → Regular user token (privilege escalation target)
* `200` on `/admin/*` → Admin token (jackpot)
* Mix of `200/403` → Token with limited scopes

---

## Disclaimer

This tool is for **educational and authorized security testing purposes only**.
Do not run against production systems without permission.
The author assumes no responsibility for misuse.

