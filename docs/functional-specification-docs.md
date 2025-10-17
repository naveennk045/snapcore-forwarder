
# Functional Specification Document (FSD)

**Instagram ⇄ YouTube Reels/Shorts Forwarding System**

***

## Document Information

**Document Title:** Functional Specification Document (FSD)
**Project Name:** Instagram-YouTube Reels Forwarding System
**Prepared For:** Client
**Prepared By:** Developer(Naveenkumar)
**Date:** October 17, 2025
**Version:** 1.0


**Purpose:** This Functional Specification Document provides a comprehensive, client-facing description of the Instagram-YouTube Reels forwarding system. It details all functional requirements, user workflows, system behaviors, and interactions with concrete examples to ensure clear understanding of how the system will operate from a user's perspective.

***

## 1. Executive Summary

The Instagram-YouTube Reels Forwarding System is a production-ready web application designed to automate the bidirectional forwarding of video content between Instagram Reels and YouTube Shorts. The system provides a secure, user-friendly administrative interface for managing multiple social media accounts, configuring forwarding connections, monitoring job execution, handling failures intelligently, and analyzing performance metrics. Built with scalability in mind, the system is designed for single-user operation initially while maintaining architectural readiness for future multi-tenant SaaS expansion.

### 1.1 Key System Capabilities

- **Bidirectional Content Forwarding**: Automatically forward Instagram Reels to YouTube Shorts and vice versa
- **Multi-Account Management**: Manage multiple Instagram and YouTube accounts from a centralized dashboard
- **Connection-Based Configuration**: Create flexible forwarding rules between source and destination accounts
- **Intelligent Job Orchestration**: Queue-based job processing with automatic retry mechanisms and failure recovery
- **Proxy Management**: Support for HTTP/HTTPS and SOCKS5 proxies with health monitoring
- **Token Management**: Secure credential storage with expiry tracking and automated alerts
- **Real-Time Notifications**: Telegram-based alerting for critical events and system status
- **Comprehensive Analytics**: Detailed performance metrics, success rates, and failure analysis
- **Video Transformations**: video upscaling and green-screen layout processing
- **Error Handling**: Automated retry with exponential backoff and CAPTCHA detection

***

## 2. System Architecture Overview

### 2.1 High-Level Architecture

The system follows a modern microservices architecture deployed using Docker containers, consisting of the following core components:[^1]

**Frontend Layer:**

- React-based single-page application (SPA)
- Responsive UI with Material UI or Tailwind CSS components
- Real-time updates via WebSocket or polling
- Session-based authentication with JWT tokens

**Backend Layer:**

- FastAPI (Python) REST API server
- Asynchronous request handling for high performance
- OpenAPI/Swagger documentation
- Secure authentication and authorization middleware

**Data Layer:**

- PostgreSQL database for metadata, accounts, connections, jobs, and logs
- Redis for caching and message brokering
- File system storage for downloaded/processed videos
- Encrypted storage for sensitive credentials

**Worker Layer:**

- Celery distributed task queue
- Multiple worker processes for concurrent job execution
- Automatic job scheduling and retry mechanisms
- Support for horizontal scaling

**Infrastructure Layer:**

- Nginx reverse proxy for HTTPS termination
- Docker Compose for container orchestration
- VPS hosting environment
- Telegram Bot API for notifications


### 2.2 System Architecture Diagram

```
┌─────────────────────────────────────────────────────────────┐
│                         CLIENT LAYER                         │
│  ┌─────────────────────────────────────────────────────┐   │
│  │          Web Browser (React Frontend)                │   │
│  └─────────────────────────────────────────────────────┘   │
└────────────────────────────┬────────────────────────────────┘
                             │ HTTPS
┌────────────────────────────▼────────────────────────────────┐
│                    NGINX REVERSE PROXY                       │
│            (HTTPS Termination, Static Assets)                │
└────────────────────────────┬────────────────────────────────┘
                             │
┌────────────────────────────▼────────────────────────────────┐
│                  BACKEND API LAYER (FastAPI)                 │
│  ┌─────────────┐  ┌──────────────┐  ┌──────────────┐       │
│  │   Auth      │  │   Account    │  │  Connection  │       │
│  │   Service   │  │   Service    │  │   Service    │       │
│  └─────────────┘  └──────────────┘  └──────────────┘       │
│  ┌─────────────┐  ┌──────────────┐  ┌──────────────┐       │
│  │    Job      │  │   Proxy      │  │  Analytics   │       │
│  │   Service   │  │   Service    │  │   Service    │       │
│  └─────────────┘  └──────────────┘  └──────────────┘       │
└────────────────────────────┬────────────────────────────────┘
                             │
         ┌───────────────────┼───────────────────┐
         │                   │                   │
┌────────▼────────┐ ┌────────▼────────┐ ┌───────▼──────────┐
│   PostgreSQL    │ │     Redis       │ │  Celery Workers  │
│    Database     │ │  (Queue/Cache)  │ │  (Job Execution) │
└─────────────────┘ └─────────────────┘ └───────┬──────────┘
                                                  │
                              ┌───────────────────┼────────────────┐
                              │                   │                │
                     ┌────────▼────────┐ ┌────────▼────────┐ ┌───▼──────┐
                     │  Instagram API  │ │  YouTube API    │ │Telegram  │
                     │  (Source/Dest)  │ │  (Source/Dest)  │ │   Bot    │
                     └─────────────────┘ └─────────────────┘ └──────────┘
```


***

## 3. User Roles \& Access Control

### 3.1 Administrator (Single User)

**Access Level:** Full system access

**Capabilities:**

- Manage all Instagram and YouTube accounts
- Create, modify, and delete connections
- Configure and test proxies
- Start, stop, pause, and manually trigger jobs
- Receive Telegram notifications -- **we will implement this in the last phase**
- Manage tokens and credentials
- Resolve CAPTCHA challenges
- Update admin password

**Authentication:** Username and password with bcrypt hashing and session/JWT token.[^1]

**Session Management:** Configurable session timeout with automatic logout on expiry.[^1]

***

## 4. Functional Requirements with Detailed Flows

### 4.1 Authentication \& Authorization Flow

**Objective:** Secure user access to the administrative interface with session management.[^1]

#### 4.1.1 Login Process Flow

**Step-by-Step Flow:**

1. **User Action:** User navigates to the login page (`/login`)
2. **System Response:** Display login form with username and password fields
3. **User Action:** User enters credentials and clicks "Login"
4. **System Validation:**
    - Backend receives POST request to `/api/login`
    - System validates username exists in database
    - System verifies password hash using bcrypt
5. **Decision Point:** Are credentials valid?
    - **If Invalid:**
        - Return HTTP 401 Unauthorized
        - Display error message: "Invalid username or password"
        - User remains on login page
    - **If Valid:**
        - Generate JWT token or session ID
        - Set secure HTTP-only cookie
        - Return HTTP 200 with token
        - Redirect user to dashboard (`/dashboard`)
6. **Session Monitoring:** System continuously checks session validity
7. **Session Timeout:** On timeout, redirect to login with message "Session expired. Please login again."

**Example Login Request:**

```json
POST /api/login
Content-Type: application/json

{
  "username": "admin",
  "password": "SecureP@ssw0rd123"
}
```

**Example Successful Response:**

```json
{
  "status": "success",
  "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "user": {
    "id": 1,
    "username": "admin"
  },
  "expires_at": "2025-10-17T18:39:00Z"
}
```


#### 4.1.2 Password Update Flow

**Step-by-Step Flow:**

1. **User Action:** Navigate to Settings → Admin Password
2. **User Action:** Enter current password, new password, and confirm new password
3. **System Validation:**
    - Verify current password is correct
    - Validate new password meets complexity requirements (min 8 characters, uppercase, lowercase, number, special character)
    - Verify new password matches confirmation
4. **Decision Point:** All validations pass?
    - **If No:** Display specific error message
    - **If Yes:**
        - Hash new password using bcrypt
        - Update password_hash in database
        - Invalidate all existing sessions
        - Display success message: "Password updated successfully. Please login again."
        - Redirect to login page

**Example Password Update Request:**

```json
PUT /api/admin/password
Authorization: Bearer <token>
Content-Type: application/json

{
  "current_password": "OldP@ssw0rd123",
  "new_password": "NewSecureP@ss456",
  "confirm_password": "NewSecureP@ss456"
}
```


***

### 4.2 Account Management Flow

**Objective:** Enable management of Instagram and YouTube accounts with secure credential storage and token handling.[^1]

#### 4.2.1 Add Instagram Account Flow

**Step-by-Step Flow:**

1. **User Action:** Navigate to Accounts → Add Account → Instagram
2. **System Response:** Display Instagram account form with fields:
    - Account Alias (user-friendly name)
    - Instagram Username
    - Authentication Method (Graph API or Current API)
    - Facebook Page ID (if Graph API selected)
    - Token Reference/Credentials
3. **User Action:** Fill form and click "Save"
4. **System Processing:**
    - Validate all required fields are populated
    - Encrypt sensitive credentials
    - Store account metadata in database
    - Create initial token expiry record if applicable
    - Assign unique account ID
5. **System Response:** Display success message "Instagram account 'TravelReels_Insta' added successfully"
6. **Background Task:** System schedules token expiry monitoring job

**Example Instagram Account Creation Request:**

```json
POST /api/accounts
Authorization: Bearer <token>
Content-Type: application/json

{
  "type": "instagram",
  "alias": "TravelReels_Insta",
  "username": "travel_reels_official",
  "auth_method": "graph_api",
  "facebook_page_id": "109234567890123",
  "credentials": {
    "access_token": "EAAG...Zc9Q",
    "token_expiry": "2025-12-17T10:00:00Z"
  }
}
```

**Example Success Response:**

```json
{
  "status": "success",
  "account": {
    "id": 15,
    "type": "instagram",
    "alias": "TravelReels_Insta",
    "username": "travel_reels_official",
    "auth_method": "graph_api",
    "status": "active",
    "token_expiry": "2025-12-17T10:00:00Z",
    "created_at": "2025-10-17T10:39:00Z"
  }
}
```


#### 4.2.2 Add YouTube Account Flow

**Step-by-Step Flow:**

1. **User Action:** Navigate to Accounts → Add Account → YouTube
2. **System Response:** Display YouTube account form with fields:
    - Account Alias
    - OAuth Client JSON Upload (drag-drop or file picker)
    - Channel ID
3. **User Action:** Enter alias and upload `client_secret.json` file
4. **System Processing:**
    - Parse JSON file to extract `client_id` and `client_secret`
    - Store JSON file securely on server filesystem
    - Generate unique token reference ID
    - Extract and store token expiry metadata
    - Insert account record into database
5. **OAuth Flow Initiation:**
    - System generates OAuth authorization URL
    - Display authorization button: "Authorize YouTube Access"
6. **User Action:** Click authorization button
7. **System Response:** Open OAuth consent screen in new tab
8. **User Action:** Grant permissions
9. **OAuth Callback:**
    - System receives authorization code
    - Exchange code for access_token and refresh_token
    - Store tokens encrypted in database
    - Update account status to "active"
10. **System Response:** Display "YouTube account 'TechShorts_YT' added and authorized successfully"

**Example YouTube Account Creation Request:**

```http
POST /api/accounts
Authorization: Bearer <token>
Content-Type: multipart/form-data

------WebKitFormBoundary7MA4YWxkTrZu0gW
Content-Disposition: form-data; name="type"

youtube
------WebKitFormBoundary7MA4YWxkTrZu0gW
Content-Disposition: form-data; name="alias"

TechShorts_YT
------WebKitFormBoundary7MA4YWxkTrZu0gW
Content-Disposition: form-data; name="channel_id"

UCabcd1234567890xyz
------WebKitFormBoundary7MA4YWxkTrZu0gW
Content-Disposition: form-data; name="oauth_client"; filename="client_secret.json"
Content-Type: application/json

{
  "installed": {
    "client_id": "123456789-abcdefg.apps.googleusercontent.com",
    "client_secret": "GOCSPX-abcd1234_efgh5678",
    "redirect_uris": ["http://localhost:8080/oauth2callback"]
  }
}
------WebKitFormBoundary7MA4YWxkTrZu0gW--
```


#### 4.2.3 Token Expiry Monitoring Flow

**Continuous Background Process:**

1. **Scheduled Task:** Every 6 hours, system scans all accounts for token expiry
2. **Check Logic:**
    - For each account, calculate days until token expiry
    - Compare with configured alert threshold (default: 2 days)
3. **Decision Point:** Token expiring within threshold?
    - **If No:** Continue monitoring
    - **If Yes:** Trigger alert process
4. **Alert Generation:**
    - Create Telegram notification
    - Update account status to "expiry_warning"
    - Log event in system logs
5. **Telegram Message Sent:** (See Section 4.7 for message format)

**Example Token Expiry Check:**

```python
# Pseudo-code for token expiry monitoring
for account in accounts:
    days_until_expiry = (account.token_expiry - now()).days
    alert_threshold = account.alert_before_days  # Default: 2
    
    if days_until_expiry <= alert_threshold and days_until_expiry > 0:
        send_telegram_alert(
            type="TOKEN_EXPIRY_WARNING",
            account=account,
            days_remaining=days_until_expiry
        )
    elif days_until_expiry <= 0:
        account.status = "token_expired"
        send_telegram_alert(
            type="TOKEN_EXPIRED",
            account=account
        )
```


***

### 4.3 Connection Management Flow

**Objective:** Configure and manage forwarding rules between source and destination accounts with flexible filtering and scheduling options.[^1]

#### 4.3.1 Create Connection Flow

**Step-by-Step Flow:**

1. **User Action:** Navigate to Connections → Create New Connection
2. **System Response:** Display connection creation wizard with steps:

**Step 1: Basic Configuration**

- Connection Name/Alias
- Connection Type: Select "Instagram → YouTube" or "YouTube → Instagram"

3. **User Input Example:**
    - Name: "Travel_Insta_to_TechShorts"
    - Type: "Instagram → YouTube"
    - Click "Next"

**Step 2: Account Selection**

- Source Account: Dropdown list of available Instagram accounts
- Destination Account: Dropdown list of available YouTube accounts

4. **User Input Example:**
    - Source: "TravelReels_Insta"
    - Destination: "TechShorts_YT"
    - Click "Next"

**Step 3: Proxy Configuration (Optional)**

- Select Proxy: Dropdown "None" or select from proxy pool
- Proxy Assignment: "Per-connection" or "Use account default"

5. **User Input Example:**
    - Select Proxy: "US_Proxy_01 (192.168.1.100:8080)"
    - Click "Next"

**Step 4: Filter Rules**

- Forward Mode:
    - [ ] Forward all new posts
    - [ ] Forward only if caption contains keywords: ____
    - [ ] Include existing/old posts (one-time sync)
- Keywords (if caption filter enabled): "tech, innovation, AI"
- Date Range (if old posts enabled): From: 2025-01-01, To: 2025-10-17

6. **User Input Example:**
    - Forward Mode: "Forward all new posts"
    - Click "Next"

**Step 5: Scheduling Options**

- Schedule Type:
    - [ ] Continuous monitoring (real-time forwarding)
    - [ ] Scheduled windows: Daily at __:__ to __:__
- Check Interval: Every 5 minutes (for continuous mode)

7. **User Input Example:**
    - Schedule Type: "Continuous monitoring"
    - Check Interval: 5 minutes
    - Click "Next"

**Step 6: Video Transform Options**

- [ ] Enable video upscaling
- [ ] Apply green-screen layout
- Video Quality: Original / Optimized / Maximum Compatibility

8. **User Input Example:**
    - Enable upscaling: Checked
    - Green-screen: Unchecked
    - Quality: "Optimized"
    - Click "Next"

**Step 7: Review \& Save**

- Display summary of all configuration
- "Save \& Activate" or "Save as Inactive"

9. **User Action:** Click "Save \& Activate"
10. **System Processing:**
    - Validate all configurations
    - Insert connection record into database
    - If "Activate" selected, set status to "active" and schedule monitoring job
    - Generate initial job for old posts if configured
    - Display success message: "Connection 'Travel_Insta_to_TechShorts' created and activated"

**Example Connection Creation Request:**

```json
POST /api/connections
Authorization: Bearer <token>
Content-Type: application/json

{
  "name": "Travel_Insta_to_TechShorts",
  "type": "instagram_to_youtube",
  "source_account_id": 15,
  "destination_account_id": 23,
  "proxy_id": 7,
  "filters": {
    "mode": "forward_all_new",
    "caption_keywords": [],
    "include_old_posts": false,
    "date_range": null
  },
  "schedule": {
    "type": "continuous",
    "check_interval_minutes": 5
  },
  "transform_options": {
    "upscale": true,
    "greenscreen": false,
    "quality": "optimized"
  },
  "status": "active"
}
```

**Example Success Response:**

```json
{
  "status": "success",
  "connection": {
    "id": 42,
    "name": "Travel_Insta_to_TechShorts",
    "type": "instagram_to_youtube",
    "source_account": {
      "id": 15,
      "alias": "TravelReels_Insta"
    },
    "destination_account": {
      "id": 23,
      "alias": "TechShorts_YT"
    },
    "proxy": {
      "id": 7,
      "alias": "US_Proxy_01"
    },
    "status": "active",
    "created_at": "2025-10-17T10:39:00Z",
    "last_run": null,
    "total_forwarded": 0,
    "success_count": 0,
    "failure_count": 0
  }
}
```


#### 4.3.2 Start/Stop/Pause Connection Flow

**Start Connection:**

1. **User Action:** Navigate to Connections list → Find connection → Click "Start" button
2. **System Validation:** Check if all accounts have valid tokens
3. **Decision Point:** All prerequisites met?
    - **If No:** Display error "Cannot start: YouTube token expired for TechShorts_YT"
    - **If Yes:**
        - Update connection status to "active"
        - Schedule monitoring job with configured interval
        - Display success toast: "Connection started successfully"
        - Background worker begins monitoring source account

**Stop Connection:**

1. **User Action:** Click "Stop" button on active connection
2. **System Processing:**
    - Update connection status to "stopped"
    - Cancel all scheduled monitoring jobs for this connection
    - Allow currently running jobs to complete
    - Display confirmation: "Connection stopped. Running jobs will complete."

**Pause Connection:**

1. **User Action:** Click "Pause" button on active connection
2. **System Processing:**
    - Update connection status to "paused"
    - Suspend monitoring (don't cancel, just pause)
    - Keep job history intact
    - Display: "Connection paused. Click Resume to continue."

**Example Start Connection Request:**

```json
POST /api/connections/42/start
Authorization: Bearer <token>

Response:
{
  "status": "success",
  "message": "Connection 'Travel_Insta_to_TechShorts' started",
  "connection_id": 42,
  "new_status": "active",
  "next_check": "2025-10-17T10:44:00Z"
}
```


#### 4.3.3 Manual "Run Now" Flow

**Objective:** Trigger immediate forwarding without waiting for scheduled checks.[^1]

**Step-by-Step Flow:**

1. **User Action:** Navigate to connection details → Click "Run Now" button
2. **System Response:** Display confirmation dialog: "Manually trigger forwarding job for all new posts?"
3. **User Action:** Click "Confirm"
4. **System Processing:**
    - Query source account for latest posts since last run
    - For each new post detected:
        - Create job record with status "queued"
        - Add job to Celery task queue
    - Display: "3 new posts found. Jobs queued for processing."
5. **Real-time Updates:** Job status updates displayed in UI as workers process jobs
6. **Completion:** Display summary: "3 jobs completed. 2 succeeded, 1 failed (retry in progress)"

**Example Run Now Request:**

```json
POST /api/connections/42/run
Authorization: Bearer <token>

Response:
{
  "status": "success",
  "message": "Manual run triggered",
  "jobs_created": [
    {
      "job_id": 1583,
      "source_post_id": "C2xYz12345_AaBbCc",
      "status": "queued"
    },
    {
      "job_id": 1584,
      "source_post_id": "C2xYz12345_DdEeFf",
      "status": "queued"
    },
    {
      "job_id": 1585,
      "source_post_id": "C2xYz12345_GgHhIi",
      "status": "queued"
    }
  ]
}
```


#### 4.3.4 Dry Run (Test Mode) Flow

**Objective:** Test connection configuration without actually posting to destination.[^1]

**Step-by-Step Flow:**

1. **User Action:** Click "Dry Run" button on connection
2. **System Response:** Display modal: "Dry run will simulate forwarding without posting. Continue?"
3. **User Action:** Confirm
4. **System Processing:**
    - Connect to source account
    - Fetch latest posts (up to 5)
    - Download videos to temporary location
    - Apply configured transformations
    - Validate destination account credentials
    - Simulate upload (prepare metadata, validate format)
    - **Do NOT actually post to destination**
    - Generate detailed report
5. **System Response:** Display dry run report:
    - Posts found: 5
    - Videos downloaded: 5 (total size: 125 MB)
    - Transformations applied: upscaling (2 videos)
    - Destination validation: Success
    - Estimated upload time: 8-12 minutes
    - Issues detected: None
6. **User Action:** Review report and click "Close"

**Example Dry Run Request:**

```json
POST /api/connections/42/dry-run
Authorization: Bearer <token>

Response:
{
  "status": "success",
  "dry_run_results": {
    "posts_found": 5,
    "posts_tested": 5,
    "videos_downloaded": 5,
    "total_size_mb": 125,
    "transformations": {
      "upscale_applied": 2,
      "greenscreen_applied": 0
    },
    "destination_validation": "passed",
    "estimated_upload_time_minutes": "8-12",
    "issues": [],
    "sample_posts": [
      {
        "source_id": "C2xYz12345_AaBbCc",
        "caption": "Amazing sunset in Bali 🌅",
        "duration_sec": 28,
        "size_mb": 24.5,
        "transformation_result": "upscaled to 1080p"
      }
    ]
  }
}
```


***

### 4.4 Proxy Management Flow

**Objective:** Manage proxy servers for account access with health monitoring and rotation policies.[^1]

#### 4.4.1 Add Proxy Flow

**Step-by-Step Flow:**

1. **User Action:** Navigate to Proxies → Add Proxy
2. **System Response:** Display proxy form with fields:
    - Proxy Alias (friendly name)
    - Proxy Type: HTTP, HTTPS, SOCKS5
    - Host/IP Address
    - Port
    - Username (optional)
    - Password (optional)
    - Assignment: Global or Per-Account
3. **User Input Example:**
    - Alias: "US_Proxy_01"
    - Type: "HTTP"
    - Host: "192.168.1.100"
    - Port: "8080"
    - Username: "proxyuser"
    - Password: "proxypass123"
    - Assignment: "Global"
4. **User Action:** Click "Save \& Test"
5. **System Processing:**
    - Validate IP/host format
    - Encrypt username and password
    - Insert proxy record into database
    - Trigger immediate health check
6. **Health Check Execution:**
    - Attempt connection through proxy
    - Test with known endpoint (e.g., httpbin.org)
    - Measure response time
    - Record result
7. **System Response:**
    - **If Success:** "Proxy 'US_Proxy_01' added successfully. Health check passed (120ms)"
    - **If Failure:** "Proxy added but health check failed: Connection timeout"

**Example Add Proxy Request:**

```json
POST /api/proxies
Authorization: Bearer <token>
Content-Type: application/json

{
  "alias": "US_Proxy_01",
  "type": "http",
  "host": "192.168.1.100",
  "port": 8080,
  "username": "proxyuser",
  "password": "proxypass123",
  "assignment": "global"
}
```

**Example Success Response:**

```json
{
  "status": "success",
  "proxy": {
    "id": 7,
    "alias": "US_Proxy_01",
    "type": "http",
    "host": "192.168.1.100",
    "port": 8080,
    "assignment": "global",
    "health_status": "healthy",
    "last_health_check": "2025-10-17T10:39:15Z",
    "response_time_ms": 120,
    "created_at": "2025-10-17T10:39:00Z"
  }
}
```


#### 4.4.2 Proxy Health Check Flow

**Manual Health Check:**

1. **User Action:** Navigate to Proxies list → Click health check icon on specific proxy
2. **System Processing:**
    - Initiate connection test through proxy
    - Attempt to reach test endpoints:
        - https://www.instagram.com (for Instagram validation)
        - https://www.youtube.com (for YouTube validation)
    - Measure latency and success rate
    - Update proxy status
3. **System Response:**
    - Display result: "Health check completed. Status: Healthy, Latency: 145ms"
    - Update last_health_check timestamp
    - If failed: Display error details and suggested action

**Automated Health Check (Background):**

- **Frequency:** Every 30 minutes for all active proxies
- **Process:**
    - Worker task iterates through all proxies
    - Performs health check for each
    - Updates status in database
    - If proxy fails 3 consecutive checks:
        - Mark as "unhealthy"
        - Send Telegram alert
        - Automatically reassign connections to healthy proxies

**Example Health Check Request:**

```json
POST /api/proxies/7/health-check
Authorization: Bearer <token>

Response:
{
  "status": "success",
  "proxy_id": 7,
  "health_status": "healthy",
  "tests": [
    {
      "endpoint": "https://www.instagram.com",
      "result": "success",
      "latency_ms": 142
    },
    {
      "endpoint": "https://www.youtube.com",
      "result": "success",
      "latency_ms": 156
    }
  ],
  "average_latency_ms": 149,
  "last_checked": "2025-10-17T10:39:30Z"
}
```


#### 4.4.3 Proxy Rotation Policy

**Configuration Options:**

- Round-robin: Cycle through proxy pool sequentially
- Random: Select random proxy for each job
- Least-used: Select proxy with fewest recent connections
- Sticky: Use same proxy for all jobs in a connection

**Example Configuration:**

```json
PUT /api/connections/42
Authorization: Bearer <token>
Content-Type: application/json

{
  "proxy_policy": {
    "mode": "round_robin",
    "pool": [7, 8, 9, 10],
    "fallback_to_direct": false,
    "max_retry_per_proxy": 2
  }
}
```


***

### 4.5 Job Orchestration \& Worker Flow

**Objective:** Queue-based job processing with monitoring, retry mechanisms, and status tracking.[^1]

#### 4.5.1 Job Creation and Queueing Flow

**Triggered by Connection Monitoring:**

1. **Scheduled Task:** Connection monitoring job runs every 5 minutes (configurable)
2. **Source Account Query:**
    - Fetch posts since last successful check
    - Compare against database to identify new posts
3. **New Post Detection:**
    - For each new post found:
        - Extract metadata (post_id, caption, media_url, timestamp)
        - Apply filter rules (caption matching, date range)
4. **Decision Point:** Does post match filters?
    - **If No:** Skip post, log as "filtered out"
    - **If Yes:** Proceed to job creation
5. **Job Creation:**
    - Generate unique job_id
    - Create job record in database:

```json
{
  "job_id": 1586,
  "connection_id": 42,
  "source_post_id": "C2xYz12345_JjKkLl",
  "source_media_url": "https://...",
  "status": "queued",
  "attempts": 0,
  "created_at": "2025-10-17T10:45:00Z"
}
```

    - Add job to Celery queue with priority
6. **Queue Assignment:** Job added to appropriate queue based on connection type

**Example Job Queue Message:**

```json
{
  "task": "forward_reel",
  "job_id": 1586,
  "connection_id": 42,
  "source_account_id": 15,
  "destination_account_id": 23,
  "source_post": {
    "id": "C2xYz12345_JjKkLl",
    "media_url": "https://instagram.com/reel/C2xYz12345_JjKkLl/media",
    "caption": "Exploring ancient temples in Cambodia 🏛️ #travel",
    "duration": 32
  },
  "transform_options": {
    "upscale": true,
    "greenscreen": false
  },
  "proxy_id": 7,
  "priority": "normal"
}
```


#### 4.5.2 Worker Job Execution Flow

**Worker Process:**

1. **Job Pickup:** Available Celery worker picks job from queue
2. **Status Update:** Update job status to "running", record start_time
3. **Step 1: Download Source Video**
    - Use proxy if configured
    - Download video from source_media_url to temporary location
    - Validate file integrity (format, size, corruption check)
    - **If download fails:** Mark job as failed, schedule retry
4. **Step 2: Apply Video Transformations**
    - Load video using FFmpeg
    - Apply upscaling if enabled (720p → 1080p or 1080p → 4K)
    - Apply green-screen layout if enabled
    - Apply automatic formatting for destination platform requirements
    - Save transformed video
5. **Step 3: Prepare Metadata for Destination**
    - Extract or modify caption
    - Add hashtags if configured
    - Set visibility (public/unlisted)
    - Prepare thumbnail if required
6. **Step 4: Upload to Destination**
    - Authenticate with destination account
    - Use proxy if configured
    - Upload video file
    - Set metadata (title, description, hashtags)
    - Handle platform-specific API requirements
7. **Step 5: Verify Upload**
    - Check upload confirmation from API
    - Verify video is accessible
    - Extract destination post ID
8. **Success Handling:**
    - Update job status to "success"
    - Record completion_time
    - Store destination_post_id
    - Delete temporary video files
    - Update connection statistics (total_forwarded++, success_count++)
    - Send success notification if configured
9. **Failure Handling:** (See Section 4.10 for detailed error handling)

**Example Job Execution Log:**

```
[2025-10-17 10:45:00] Job 1586: Status changed to 'running'
[2025-10-17 10:45:01] Job 1586: Downloading video from Instagram...
[2025-10-17 10:45:08] Job 1586: Download complete (24.5 MB, 32 seconds)
[2025-10-17 10:45:09] Job 1586: Applying transformations (upscale: true)
[2025-10-17 10:45:23] Job 1586: Transformation complete (output: 42.1 MB, 1080p)
[2025-10-17 10:45:24] Job 1586: Preparing metadata for YouTube...
[2025-10-17 10:45:25] Job 1586: Uploading to YouTube (channel: TechShorts_YT)
[2025-10-17 10:46:12] Job 1586: Upload complete (YouTube Short ID: dQw4w9WgXcQ)
[2025-10-17 10:46:13] Job 1586: Verifying upload...
[2025-10-17 10:46:15] Job 1586: Verification successful
[2025-10-17 10:46:16] Job 1586: Cleaning up temporary files
[2025-10-17 10:46:17] Job 1586: Status changed to 'success'
[2025-10-17 10:46:17] Job 1586: Total execution time: 1m 17s
```


#### 4.5.3 Real-Time Job Status Monitoring

**WebSocket Updates (Preferred):**

1. **Client Connection:** Frontend establishes WebSocket connection to `/ws/jobs`
2. **Subscription:** Client subscribes to updates for specific connection or all jobs
3. **Worker Events:** As worker processes job, emit events to WebSocket
4. **Client Display:** UI updates in real-time showing:
    - Job status changes
    - Progress percentage (download, transform, upload phases)
    - Current step description
    - Estimated time remaining

**Polling Alternative:**

1. **Frontend Polling:** Every 5 seconds, call `GET /api/jobs?status=running,queued`
2. **Backend Response:** Return current status of active jobs
3. **UI Update:** Refresh job list and progress indicators

**Example WebSocket Message:**

```json
{
  "event": "job_status_update",
  "timestamp": "2025-10-17T10:45:25Z",
  "job": {
    "job_id": 1586,
    "connection_id": 42,
    "status": "running",
    "current_step": "uploading",
    "progress_percent": 75,
    "message": "Uploading to YouTube (32 MB / 42 MB)",
    "estimated_completion": "2025-10-17T10:46:10Z"
  }
}
```


***

### 4.6 Token \& Credential Management Flow

**Objective:** Securely manage OAuth tokens and API credentials with expiry tracking and automated alerts.[^1]

#### 4.6.1 YouTube Token Upload and OAuth Flow

**Step-by-Step Flow:**

1. **User Action:** Navigate to Accounts → Select YouTube account → Click "Update Token"
2. **System Response:** Display token upload interface with two options:
    - Upload new client_secret.json file
    - Re-authorize with existing credentials
3. **Option A: Upload New Client JSON**
    - **User Action:** Drag-drop or select `client_secret_12345.json`
    - **System Processing:**
        - Parse JSON to extract client_id and client_secret
        - Validate JSON structure
        - Store file securely at `/app/secrets/youtube_tokens/account_23.json`
        - Generate OAuth authorization URL
    - **System Response:** Display "Authorize with YouTube" button
4. **OAuth Authorization Process:**
    - **User Action:** Click "Authorize with YouTube"
    - **System Response:** Open OAuth consent screen in popup/new tab
    - **Consent Screen:** Google OAuth page requesting permissions:
        - View YouTube account
        - Manage YouTube videos
        - Upload videos
    - **User Action:** Click "Allow"
    - **OAuth Callback:**
        - Google redirects to `https://yourapp.com/oauth2callback?code=4/0AX4Xf...`
        - Backend receives authorization code
        - Exchange code for tokens:

```python
POST https://oauth2.googleapis.com/token
{
  "code": "4/0AX4Xf...",
  "client_id": "...",
  "client_secret": "...",
  "redirect_uri": "https://yourapp.com/oauth2callback",
  "grant_type": "authorization_code"
}
```

        - Receive response:

```json
{
  "access_token": "ya29.a0AfH6SM...",
  "refresh_token": "1//0gN7s...",
  "expires_in": 3599,
  "scope": "https://www.googleapis.com/auth/youtube...",
  "token_type": "Bearer"
}
```

        - Encrypt and store tokens in database
        - Calculate and store token_expiry (now + expires_in)
        - Update account status to "active"
5. **System Response:**
    - Close popup
    - Display success message: "YouTube account authorized successfully. Token expires: 2025-10-18 11:45:00"
    - Send Telegram notification: "YouTube token updated for account 'TechShorts_YT'"

**Example Token Storage (Encrypted):**

```json
{
  "account_id": 23,
  "token_type": "youtube_oauth",
  "client_id": "123456789-abcdefg.apps.googleusercontent.com",
  "client_secret_encrypted": "AES256:gAAAAABfK...",
  "access_token_encrypted": "AES256:gAAAAABfK...",
  "refresh_token_encrypted": "AES256:gAAAAABfK...",
  "token_expiry": "2025-10-18T11:45:00Z",
  "scopes": [
    "https://www.googleapis.com/auth/youtube.upload",
    "https://www.googleapis.com/auth/youtube"
  ],
  "last_refreshed": "2025-10-17T10:45:00Z"
}
```


#### 4.6.2 Token Refresh Flow (Automatic)

**Background Process:**

1. **Scheduled Task:** Every hour, check for tokens expiring within next 6 hours
2. **Token Selection:** Identify YouTube tokens with `expires_at < now + 6 hours`
3. **For Each Expiring Token:**
    - Attempt automatic refresh using refresh_token
    - Request:

```python
POST https://oauth2.googleapis.com/token
{
  "refresh_token": "1//0gN7s...",
  "client_id": "...",
  "client_secret": "...",
  "grant_type": "refresh_token"
}
```

    - **If Refresh Success:**
        - Update access_token with new token
        - Update token_expiry with new expiry
        - Log successful refresh
        - Send Telegram notification: "Token auto-refreshed for 'TechShorts_YT'"
    - **If Refresh Failure:**
        - Mark token as "refresh_failed"
        - Pause all connections using this account
        - Send Telegram alert (see Section 4.7.2)
        - Update account status to "requires_reauth"

#### 4.6.3 Token Expiry Alert Configuration

**User Configuration:**

1. **User Action:** Navigate to Account Settings → Select account → Alert Settings
2. **Configuration Options:**
    - Enable expiry alerts: [x]
    - Send alert before expiry:  days
    - Alert channels: [x] Telegram [ ] Email
3. **User Action:** Click "Save Alert Settings"
4. **System Processing:** Update account alert preferences in database

**Alert Timing Examples:**

- Token expires: 2025-10-19 10:00:00
- Alert threshold: 2 days
- Alert sent: 2025-10-17 10:00:00
- Message: "YouTube token for 'TechShorts_YT' expires in 2 days. Please re-authorize."

***

### 4.7 Notification \& Alert Flow

**Objective:** Send real-time Telegram notifications for critical events with structured, actionable messages.[^1]

#### 4.7.1 Telegram Configuration

**Initial Setup:**

1. **Admin Configuration:** Navigate to Settings → Notifications → Telegram
2. **Configuration Fields:**
    - Bot Token: `1234567890:ABCdefGHIjklMNOpqrsTUVwxyz`
    - Channel ID: `@your_channel` or `-1001234567890`
    - Test Connection button
3. **User Action:** Enter credentials and click "Test Connection"
4. **System Processing:**
    - Send test message to Telegram channel via Bot API
    - Verify delivery
5. **System Response:** Display "Test message sent successfully" or error details

**Example Telegram Configuration Request:**

```json
PUT /api/settings/telegram
Authorization: Bearer <token>
Content-Type: application/json

{
  "bot_token": "1234567890:ABCdefGHIjklMNOpqrsTUVwxyz",
  "channel_id": "-1001234567890",
  "enabled": true
}
```


#### 4.7.2 Token Expiry Alert Message

**Trigger:** Token expiry detected or refresh failure

**Message Format:**

```
🔴 [SnapcoreForwarder] 🚨 ALERT: ACCESS TOKEN EXPIRED

Connection: Insta→YouTube - "Travel_Insta_to_TechShorts"
Source: TravelReels_Insta (Instagram)
Destination: TechShorts_YT (YouTube)
Time: 2025-10-17 10:45:00 IST
Token type: YouTube OAuth Access Token
Status: EXPIRED
Action: Re-authenticate in UI → Accounts → TechShorts_YT → Update Token

🔗 View in Dashboard: https://yourapp.com/accounts/23
```

**Implementation:**

```python
def send_token_expiry_alert(account, connection):
    message = f"""
🔴 [SnapcoreForwarder] 🚨 ALERT: ACCESS TOKEN EXPIRED

Connection: {connection.type_display} - "{connection.name}"
Source: {connection.source_account.alias} ({connection.source_account.type})
Destination: {connection.destination_account.alias} ({connection.destination_account.type})
Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S IST')}
Token type: {account.token_type_display}
Status: EXPIRED
Action: Re-authenticate in UI → Accounts → {account.alias} → Update Token

🔗 View in Dashboard: {DASHBOARD_URL}/accounts/{account.id}
    """
    
    send_telegram_message(
        chat_id=TELEGRAM_CHANNEL_ID,
        text=message,
        parse_mode="HTML"
    )
```


#### 4.7.3 Job Failure Alert Message

**Trigger:** Job fails after all retry attempts exhausted

**Message Format:**

```
⚠️ [SnapcoreForwarder] 🚨 ALERT: JOB FAILED

Connection: Insta→YouTube - "Travel_Insta_to_TechShorts"
Source: TravelReels_Insta (Instagram)
Destination: TechShorts_YT (YouTube)
Time: 2025-10-17 10:50:00 IST
Job ID: 1586
Error: API rate limit exceeded (403 Forbidden)
Details: YouTube API quota exceeded. Daily limit: 10,000 units. Current usage: 10,100 units.

Suggested Solution:
- Wait 24 hours for quota reset
- OR upgrade YouTube API quota
- OR distribute uploads across multiple accounts

Retry attempts: 3/3 (exhausted)
Status: MOVED TO DEAD-LETTER QUEUE

🔗 View Job Details: https://yourapp.com/jobs/1586
🔗 View Logs: https://yourapp.com/logs?job_id=1586
```


#### 4.7.4 CAPTCHA Detection Alert Message

**Trigger:** CAPTCHA encountered during Instagram login or upload

**Message Format:**

```
🤖 [SnapcoreForwarder] 🚨 CAPTCHA DETECTED (Manual Action Required)

Account: TravelReels_Insta (Instagram)
Connection: Insta→YouTube - "Travel_Insta_to_TechShorts"
Job ID: 1587
Time: 2025-10-17 11:00:00 IST
Description: CAPTCHA challenge encountered during Instagram login. Automated solving not available.

Action Required:
1. Open Instagram account manually in browser
2. Complete CAPTCHA challenge
3. Return to admin UI → Accounts → TravelReels_Insta
4. Click "Mark CAPTCHA Solved" button
5. Connection will resume automatically

⚠️ Connection paused until CAPTCHA is resolved.

🔗 Mark as Solved: https://yourapp.com/accounts/15/captcha-resolve
🔗 View Job: https://yourapp.com/jobs/1587
```


#### 4.7.5 CAPTCHA Resolved Success Message

**Trigger:** Admin marks CAPTCHA as solved and job resumes successfully

**Message Format:**

```
✅ [SnapcoreForwarder] ✨ RESOLVED: CAPTCHA SOLVED

Account: TravelReels_Insta (Instagram)
Connection: Insta→YouTube - "Travel_Insta_to_TechShorts"
Job ID: 1587
Resolved Time: 2025-10-17 11:15:00 IST
Resolution: Admin manually resolved CAPTCHA

Status: Job resumed and completed successfully
Destination Post: https://youtube.com/shorts/dQw4w9WgXcQ

Connection status: ACTIVE (monitoring resumed)
```


#### 4.7.6 Job Success After Retry Alert

**Trigger:** Job succeeds after one or more failures

**Message Format:**

```
✅ [SnapcoreForwarder] 🎉 RESOLVED: JOB SUCCEEDED AFTER RETRY

Connection: Insta→YouTube - "Travel_Insta_to_TechShorts"
Job ID: 1588
Time: 2025-10-17 11:20:00 IST
Initial Failure: Network timeout (proxy connection lost)
Retry Attempts: 2
Final Status: SUCCESS

Details: Job completed successfully on attempt 3 after proxy failover to US_Proxy_02

Source Post: C2xYz12345_MmNnOo
Destination: https://youtube.com/shorts/xYz9AbCdEfG

🔗 View Job: https://yourapp.com/jobs/1588
```


#### 4.7.7 Proxy Health Failure Alert

**Trigger:** Proxy fails health check 3 consecutive times

**Message Format:**

```
🔴 [SnapcoreForwarder] 🚨 ALERT: PROXY HEALTH CHECK FAILED

Proxy: US_Proxy_01 (192.168.1.100:8080)
Status: UNHEALTHY
Failed Checks: 3 consecutive
Last Success: 2025-10-17 09:30:00 IST
Error: Connection timeout after 30 seconds

Affected Connections:
- Travel_Insta_to_TechShorts (paused)
- FoodReels_to_CookingShorts (paused)

Action Taken:
- Proxy marked as unhealthy
- Affected connections paused
- Future jobs will use fallback proxies

Recommended Action:
1. Check proxy server status
2. Verify proxy credentials
3. Test proxy manually
4. Update or remove proxy from system

🔗 Proxy Settings: https://yourapp.com/proxies/7
```


***

### 4.8 Analytics \& Monitoring Flow

**Objective:** Provide comprehensive performance metrics, failure analysis, and operational insights with exportable reports.[^1]

#### 4.8.1 Dashboard Overview

**Dashboard Components:**

1. **High-Level Metrics (Top Section):**
    - Total Connections: 12 (8 active, 3 paused, 1 stopped)
    - Total Jobs (Last 24h): 347
    - Success Rate (Last 24h): 94.2% (327 succeeded, 20 failed)
    - Active Workers: 5/8
    - Queue Length: 12 jobs pending
2. **Real-Time Activity Feed:**
    - Recent job completions scrolling list
    - Color-coded by status (green: success, red: failed, yellow: retrying)
    - Example entries:

```
10:52 AM ✅ Job 1589 completed (Travel_Insta_to_TechShorts)
10:51 AM ⚠️ Job 1590 failed - retry 1/3 (FoodReels_to_YT)
10:50 AM ✅ Job 1591 completed (TechNews_YT_to_Insta)
```

3. **Connection Status Grid:**
    - Card for each connection showing:
        - Connection name
        - Status indicator (green dot: active, gray: stopped, yellow: paused)
        - Last run timestamp
        - Success rate (last 7 days)
        - Quick actions (Start/Stop/View)
4. **Quick Actions Panel:**
    - Create New Connection button
    - Add Account button
    - View All Logs button
    - Export Analytics button

**Example Dashboard API Response:**

```json
GET /api/dashboard/summary

{
  "connections": {
    "total": 12,
    "active": 8,
    "paused": 3,
    "stopped": 1
  },
  "jobs_24h": {
    "total": 347,
    "succeeded": 327,
    "failed": 20,
    "retrying": 5,
    "success_rate": 94.2
  },
  "workers": {
    "active": 5,
    "total_capacity": 8,
    "utilization_percent": 62.5
  },
  "queue": {
    "pending_jobs": 12,
    "avg_wait_time_seconds": 45
  },
  "recent_activity": [
    {
      "timestamp": "2025-10-17T10:52:00Z",
      "job_id": 1589,
      "connection_name": "Travel_Insta_to_TechShorts",
      "status": "success"
    }
  ]
}
```


#### 4.8.2 Connection-Level Analytics

**User Action:** Click on connection card → View detailed analytics

**Analytics Views:**

**1. Performance Metrics (Time Period Selectable: 7 days, 30 days, 90 days)**

- Total Jobs Forwarded: 1,247
- Successful: 1,189 (95.3%)
- Failed: 58 (4.7%)
- Average Retry Count: 1.2
- Average Job Duration: 2m 15s
- Peak Processing Time: 3:00 PM - 5:00 PM IST

**2. Failure Analysis:**

- Top Failure Reasons (Bar Chart):
    - Token Expired: 24 (41.4%)
    - API Rate Limit: 15 (25.9%)
    - Network Timeout: 10 (17.2%)
    - Proxy Error: 6 (10.3%)
    - CAPTCHA: 3 (5.2%)

**3. Timeline View (Line Chart):**

- X-axis: Date
- Y-axis: Job count
- Lines: Success (green), Failed (red), Total (blue)

**4. Uptime Calendar:**

- Calendar heat map showing daily success rates
- Green: >95% success, Yellow: 80-95%, Red: <80%

**Example Connection Analytics Request:**

```json
GET /api/analytics/connection/42?period=30days

{
  "connection_id": 42,
  "connection_name": "Travel_Insta_to_TechShorts",
  "period": {
    "start": "2025-09-17",
    "end": "2025-10-17"
  },
  "metrics": {
    "total_jobs": 1247,
    "succeeded": 1189,
    "failed": 58,
    "success_rate": 95.3,
    "avg_retry_count": 1.2,
    "avg_job_duration_seconds": 135
  },
  "failure_breakdown": [
    {"reason": "token_expired", "count": 24, "percent": 41.4},
    {"reason": "api_rate_limit", "count": 15, "percent": 25.9},
    {"reason": "network_timeout", "count": 10, "percent": 17.2},
    {"reason": "proxy_error", "count": 6, "percent": 10.3},
    {"reason": "captcha", "count": 3, "percent": 5.2}
  ],
  "daily_stats": [
    {"date": "2025-10-17", "total": 45, "succeeded": 43, "failed": 2},
    {"date": "2025-10-16", "total": 42, "succeeded": 40, "failed": 2}
  ]
}
```


#### 4.8.3 Account-Level Analytics

**User Action:** Navigate to Accounts → Select account → View Analytics

**Metrics Displayed:**

1. **Account Health Score:** 92/100
    - Success rate: 95.3%
    - Uptime: 98.5%
    - Token status: Valid
    - Last failure: 2 days ago
2. **Usage Statistics:**
    - Total Posts Forwarded: 2,456
    - As Source: 1,247 jobs
    - As Destination: 1,209 jobs
    - Active Connections: 3
3. **Connected Accounts:**
    - List of connections using this account
    - Status and performance for each
4. **Error History:**
    - Timeline of failures associated with this account
    - Categorized by error type

**Example Account Analytics Request:**

```json
GET /api/analytics/account/15?period=90days

{
  "account_id": 15,
  "account_alias": "TravelReels_Insta",
  "account_type": "instagram",
  "health_score": 92,
  "metrics": {
    "total_forwarded": 2456,
    "as_source": 1247,
    "as_destination": 1209,
    "success_rate": 95.3,
    "uptime_percent": 98.5
  },
  "connections": [
    {
      "connection_id": 42,
      "name": "Travel_Insta_to_TechShorts",
      "role": "source",
      "status": "active",
      "success_rate": 95.3
    }
  ],
  "token_status": {
    "valid": true,
    "expires_at": "2025-12-17T10:00:00Z",
    "days_until_expiry": 61
  }
}
```


#### 4.8.4 System-Wide Analytics

**User Action:** Navigate to Analytics → System Overview

**Dashboard Sections:**

**1. Monthly Summary:**

- Total Jobs: 10,542
- Success: 9,987 (94.7%)
- Failed: 555 (5.3%)
- Total Video Size Processed: 523 GB
- Average Job Duration: 2m 08s

***

### 4.9 Video Processing Flow

**Objective:** Transform videos to meet destination platform requirements with optional enhancements.[^1]

#### 4.9.1 Video Upscaling Flow

**Configuration:** Enabled at connection level

**Processing Steps:**

1. **Input Video Analysis:**
    - Detect current resolution (e.g., 720x1280)
    - Detect frame rate (e.g., 30 fps)
    - Detect codec (e.g., H.264)
    - Check video duration and file size
2. **Up-scaling Decision:**
    - If resolution < 1080p AND upscaling enabled:
        - Target resolution: 1080x1920 (Full HD)
    - If resolution >= 1080p AND upscaling enabled:
        - Target resolution: 2160x3840 (4K)
3. **FFmpeg Command Construction:**

```bash
ffmpeg -i input.mp4 \
  -vf "scale=1080:1920:flags=lanczos" \
  -c:v libx264 \
  -preset slow \
  -crf 18 \
  -c:a copy \
  -movflags +faststart \
  output.mp4
```

4. **Processing Execution:**
    - Execute FFmpeg command
    - Monitor progress (update job progress percentage)
    - Validate output file integrity
5. **Quality Verification:**
    - Check output resolution matches target
    - Verify file isn't corrupted
    - Compare file size (should increase with upscaling)
6. **Output:**
    - Original file: 24.5 MB, 720p
    - Upscaled file: 42.1 MB, 1080p

**Example Upscaling Log:**

```
[2025-10-17 10:45:09] Video upscaling initiated
[2025-10-17 10:45:09] Input: 720x1280, 30fps, H.264, 24.5 MB
[2025-10-17 10:45:09] Target: 1080x1920, 30fps, H.264
[2025-10-17 10:45:10] FFmpeg command: ffmpeg -i input.mp4 -vf scale=1080:1920...
[2025-10-17 10:45:10] Processing: [=========>        ] 45%
[2025-10-17 10:45:18] Processing: [==================] 100%
[2025-10-17 10:45:19] Output: 1080x1920, 30fps, H.264, 42.1 MB
[2025-10-17 10:45:19] Quality check: PASSED
[2025-10-17 10:45:19] Upscaling complete (duration: 10 seconds)
```


#### 4.9.2 Green-Screen Layout Flow

**Configuration:** Enabled at connection level

**Processing Steps:**

1. **Layout Selection:**
    - Green-screen layout applies specific visual template
    - Common templates:
        - Split-screen with background
        - Picture-in-picture with border
        - Full-screen with branded overlay
2. **FFmpeg Complex Filter:**

```bash
ffmpeg -i input.mp4 -i background.png \
  -filter_complex "[^1][^0]scale2ref=w=iw:h=ih[bg][vid]; \
                   [bg][vid]overlay=(W-w)/2:(H-h)/2" \
  -c:v libx264 -preset medium -crf 20 \
  output.mp4
```

3. **Processing:**
    - Apply green-screen template
    - Composite video with background/overlay
    - Maintain aspect ratio
4. **Output:**
    - Video with applied green-screen effect

**Example Green-Screen Configuration:**

```json
{
  "greenscreen": {
    "enabled": true,
    "template": "split_screen",
    "background_image": "/templates/bg_travel.png",
    "position": "center",
    "border_color": "#000000",
    "border_width": 2
  }
}
```


#### 4.9.3 Automatic Format Compliance

**Objective:** Ensure video meets destination platform requirements

**Platform Requirements:**

**Instagram Reels:**

- Aspect Ratio: 9:16 (vertical)
- Max Duration: 90 seconds
- Resolution: 1080x1920 recommended
- Format: MP4 (H.264)
- Max File Size: 100 MB

**YouTube Shorts:**

- Aspect Ratio: 9:16 (vertical)
- Max Duration: 60 seconds
- Resolution: 1080x1920 or 2160x3840
- Format: MP4 (H.264)
- Max File Size: 256 MB

**Compliance Processing:**

1. **Duration Check:**
    - If video > max duration: Trim to max duration or reject
    - Example: 75-second video for YouTube Shorts → trim to 60 seconds
2. **Aspect Ratio Check:**
    - If video != 9:16: Apply letterboxing or cropping
    - Example: 16:9 video → crop to 9:16 or add black bars
3. **File Size Check:**
    - If file size > max: Re-encode with higher compression
    - Example: 120 MB file for Instagram → re-encode to 95 MB
4. **Format Check:**
    - If format != MP4 H.264: Transcode to compatible format

**Example Compliance FFmpeg Command:**

```bash
ffmpeg -i input.mp4 \
  -vf "scale=1080:1920:force_original_aspect_ratio=decrease,pad=1080:1920:(ow-iw)/2:(oh-ih)/2" \
  -t 60 \
  -fs 250M \
  -c:v libx264 -preset medium -crf 23 \
  -c:a aac -b:a 128k \
  output.mp4
```


***

### 4.10 Error Handling \& Retry Flow

**Objective:** Automatically recover from transient failures using intelligent retry strategies with exponential backoff.[^1]

#### 4.10.1 Retry Policy Configuration

**System Defaults:**

- Max Retry Attempts: 3
- Backoff Strategy: Exponential
- Backoff Schedule:
    - Attempt 1 → Wait 10 seconds
    - Attempt 2 → Wait 60 seconds (1 minute)
    - Attempt 3 → Wait 300 seconds (5 minutes)

**Configurable Per-Connection:**

```json
{
  "retry_policy": {
    "max_attempts": 3,
    "backoff_strategy": "exponential",
    "backoff_multiplier": 6,
    "initial_delay_seconds": 10,
    "max_delay_seconds": 600,
    "retry_on_errors": [
      "network_timeout",
      "proxy_error",
      "api_temporary_error",
      "rate_limit_exceeded"
    ],
    "no_retry_on_errors": [
      "invalid_credentials",
      "account_suspended",
      "video_too_large",
      "copyright_violation"
    ]
  }
}
```


#### 4.10.2 Failure Detection and Classification

**Job Failure Triggers:**

1. **Network Errors:**
    - Connection timeout
    - DNS resolution failure
    - SSL/TLS handshake failure
    - Socket errors
2. **API Errors:**
    - HTTP 429 (Rate Limit Exceeded)
    - HTTP 500 (Internal Server Error)
    - HTTP 502/503 (Service Unavailable)
    - HTTP 401 (Unauthorized) - usually non-retriable
3. **Platform-Specific Errors:**
    - Instagram: "challenge_required" (CAPTCHA)
    - YouTube: "quota_exceeded"
    - Instagram: "login_required"
4. **File Processing Errors:**
    - Video codec unsupported
    - File corruption
    - FFmpeg processing failure
5. **Proxy Errors:**
    - Proxy authentication failed
    - Proxy connection timeout
    - Proxy returned error

**Error Classification:**

```python
ERROR_TYPES = {
    "network_timeout": {"retriable": True, "severity": "medium"},
    "api_rate_limit": {"retriable": True, "severity": "high"},
    "token_expired": {"retriable": False, "severity": "critical"},
    "proxy_error": {"retriable": True, "severity": "medium"},
    "captcha_detected": {"retriable": False, "severity": "high"},
    "video_too_large": {"retriable": False, "severity": "low"},
    "account_suspended": {"retriable": False, "severity": "critical"}
}
```


#### 4.10.3 Retry Execution Flow

**Step-by-Step Flow:**

1. **Job Execution Attempt:**
    - Worker executes job
    - Job fails with error: "Network timeout during upload"
2. **Error Analysis:**
    - Classify error type: "network_timeout"
    - Check error retriability: retriable = True
    - Get current attempt count: attempts = 1
3. **Decision Point:** Should retry?
    - Check: attempts < max_attempts? Yes (1 < 3)
    - Check: error_type in retry_on_errors? Yes
    - Decision: RETRY
4. **Backoff Calculation:**
    - Calculate delay: initial_delay * (multiplier ^ (attempts - 1))
    - Attempt 1: 10 * (6 ^ 0) = 10 seconds
    - Attempt 2: 10 * (6 ^ 1) = 60 seconds
    - Attempt 3: 10 * (6 ^ 2) = 600 seconds (capped at max_delay)
5. **Update Job Record:**

```json
{
  "job_id": 1590,
  "status": "retrying",
  "attempts": 1,
  "last_error": "network_timeout",
  "last_error_message": "Connection timeout during upload to YouTube",
  "next_retry_at": "2025-10-17T10:51:10Z"
}
```

6. **Send Alert (First Failure):**
    - Send Telegram notification: "Job 1590 failed - retry 1/3"
7. **Schedule Retry:**
    - Add job back to queue with delay
    - Worker will pick up job after delay expires
8. **Retry Attempt:**
    - Worker executes job again
    - Increment attempts = 2
9. **Outcome Scenarios:**

**Scenario A: Retry Succeeds**
    - Job completes successfully
    - Update status to "success"
    - Send success notification: "Job 1590 succeeded after 2 attempts"
    - Update connection statistics

**Scenario B: Retry Fails Again (Same Error)**
    - Classify error again: still "network_timeout"
    - Check: attempts < max_attempts? Yes (2 < 3)
    - Calculate next backoff: 60 seconds
    - Schedule another retry
    - Send alert: "Job 1590 failed - retry 2/3"

**Scenario C: Max Retries Exhausted**
    - attempts = 3
    - Check: attempts < max_attempts? No (3 = 3)
    - Decision: FAIL PERMANENTLY
    - Update status to "failed"
    - Move to dead-letter queue
    - Send final failure alert with suggested action

**Scenario D: Non-Retriable Error**
    - Error changes to "token_expired"
    - Check retriability: retriable = False
    - Decision: FAIL IMMEDIATELY (no more retries)
    - Update status to "failed"
    - Send critical alert
    - Pause connection

**Example Retry Flow Timeline:**

```
10:45:00 - Job 1590 started (attempt 1)
10:46:30 - Job 1590 failed: network_timeout
10:46:31 - Retry scheduled for 10:46:41 (10 sec delay)
10:46:31 - Telegram alert sent: "Job 1590 failed - retry 1/3"

10:46:41 - Job 1590 started (attempt 2)
10:48:15 - Job 1590 failed: network_timeout
10:48:16 - Retry scheduled for 10:49:16 (60 sec delay)
10:48:16 - Telegram alert sent: "Job 1590 failed - retry 2/3"

10:49:16 - Job 1590 started (attempt 3)
10:50:45 - Job 1590 succeeded
10:50:46 - Telegram alert sent: "Job 1590 succeeded after 3 attempts"
```


#### 4.10.4 Dead-Letter Queue Management

**Purpose:** Store permanently failed jobs for manual investigation and retry.[^1]

**Dead-Letter Queue Criteria:**

- Max retry attempts exhausted
- Non-retriable critical errors
- Manual administrator decision

**Dead-Letter Queue View:**

**User Action:** Navigate to Jobs → Dead-Letter Queue

**Display:**

- List of permanently failed jobs
- Columns:
    - Job ID
    - Connection Name
    - Source Post
    - Final Error
    - Attempts
    - Failed At
    - Actions (View Details, Manual Retry, Delete)

**Manual Retry from Dead-Letter Queue:**

1. **User Action:** Click "Manual Retry" on dead-letter job
2. **System Prompt:** "Manually retry job 1591? This will create a new job with same parameters."
3. **User Action:** Confirm
4. **System Processing:**
    - Create new job record (new job_id)
    - Copy parameters from failed job
    - Reset attempts to 0
    - Set status to "queued"
    - Add to worker queue
5. **System Response:** "New job 1595 created and queued for retry"

**Example Dead-Letter Queue API:**

```json
GET /api/jobs/dead-letter

{
  "total_count": 15,
  "jobs": [
    {
      "job_id": 1591,
      "connection_id": 42,
      "connection_name": "Travel_Insta_to_TechShorts",
      "source_post_id": "C2xYz12345_SsTtUu",
      "final_error": "api_rate_limit",
      "error_message": "YouTube API quota exceeded. Daily limit: 10,000 units.",
      "attempts": 3,
      "failed_at": "2025-10-17T10:55:00Z",
      "can_retry": true
    }
  ]
}
```


***

### 4.11 CAPTCHA Detection \& Resolution Flow

**Objective:** Detect CAPTCHA challenges, pause automation, alert administrator, and provide manual resolution interface.[^1]

#### 4.11.1 CAPTCHA Detection

**Detection Triggers:**

1. **Instagram API Response:**
    - Response contains: `"challenge_required": true`
    - Response contains: `"checkpoint_url": "https://..."`
    - HTTP 400 with message: "challenge_required"
2. **Page Content Analysis:**
    - HTML response contains CAPTCHA iframe
    - Presence of reCAPTCHA elements
    - Specific error codes from Instagram API
3. **Behavioral Detection:**
    - Multiple failed login attempts
    - Unusual access patterns detected by platform

**Example CAPTCHA Detection Code:**

```python
def detect_captcha(response):
    # Check API response
    if response.get('challenge_required'):
        return True, 'challenge_required', response.get('checkpoint_url')
    
    # Check for specific error messages
    if 'Please complete this check' in response.text:
        return True, 'recaptcha_detected', None
    
    # Check for checkpoint redirect
    if response.status_code == 302 and '/challenge/' in response.headers.get('Location', ''):
        return True, 'checkpoint_redirect', response.headers['Location']
    
    return False, None, None
```


#### 4.11.2 CAPTCHA Handling Flow

**Step-by-Step Flow:**

1. **CAPTCHA Detected During Job Execution:**
    - Worker detects CAPTCHA response from Instagram API
    - Extract CAPTCHA details (type, URL)
2. **Immediate Actions:**
    - **Pause Job:** Set job status to "captcha_pending"
    - **Pause Account:** Set account status to "captcha_detected"
    - **Pause All Connections:** Pause all connections using this account
    - **Log Event:** Create detailed log entry
3. **Alert Generation:**
    - Create Telegram alert with CAPTCHA details (see Section 4.7.4)
    - Include resolution instructions
    - Provide UI link for marking CAPTCHA as solved
4. **Administrator Notification:**
    - Alert sent to Telegram channel
    - UI displays banner: "⚠️ CAPTCHA detected on TravelReels_Insta. Action required."
5. **Manual Resolution by Administrator:**

**Step A: Admin Reviews Alert**
    - Reads Telegram message or UI notification
    - Understands which account needs attention

**Step B: Admin Opens Instagram Manually**
    - Opens Instagram in web browser
    - Logs in to affected account (TravelReels_Insta)
    - Completes CAPTCHA challenge manually
    - Verifies successful login

**Step C: Admin Marks CAPTCHA as Solved in UI**
    - Navigate to Accounts → TravelReels_Insta
    - See CAPTCHA warning banner: "CAPTCHA detected. Mark as solved after completing challenge."
    - Click "Mark CAPTCHA Solved" button
6. **System Response to Resolution:**
    - Update account status to "active"
    - Resume all paused connections for this account
    - Change job status from "captcha_pending" to "queued"
    - Re-add job to worker queue for retry
    - Send Telegram success notification (see Section 4.7.5)
7. **Job Retry After Resolution:**
    - Worker picks up job again
    - Attempts execution with fresh session
    - If successful: Complete normally
    - If CAPTCHA appears again: Repeat process

**Example CAPTCHA Resolution UI:**

**Accounts Page - CAPTCHA Warning:**

```
┌─────────────────────────────────────────────────────────┐
│ ⚠️ CAPTCHA DETECTED                                     │
│                                                          │
│ Account: TravelReels_Insta                              │
│ Detected: 2025-10-17 11:00:00 IST                       │
│ Affected Connections: 3 (paused)                        │
│ Pending Jobs: 5                                         │
│                                                          │
│ Instructions:                                           │
│ 1. Open Instagram in your browser                      │
│ 2. Log in to account: travel_reels_official            │
│ 3. Complete the CAPTCHA challenge                      │
│ 4. Verify successful login                             │
│ 5. Click button below to resume automation             │
│                                                          │
│ [Mark CAPTCHA Solved]  [View Affected Jobs]            │
└─────────────────────────────────────────────────────────┘
```

**API Endpoint for Marking CAPTCHA Solved:**

```json
POST /api/accounts/15/captcha-resolve
Authorization: Bearer <token>

{
  "resolved": true,
  "resolution_notes": "Manually completed CAPTCHA via web browser",
  "resume_connections": true
}

Response:
{
  "status": "success",
  "message": "CAPTCHA marked as solved for TravelReels_Insta",
  "account_status": "active",
  "connections_resumed": [42, 58, 71],
  "jobs_requeued": [1587, 1592, 1593, 1594, 1595]
}
```


#### 4.11.3 Third-Party CAPTCHA Solver Integration (Optional)

**Purpose:** Automate CAPTCHA solving using paid services.[^1]

**Supported Services (for investigation):**

- 2Captcha (https://2captcha.com)
- Anti-Captcha (https://anti-captcha.com)
- CapMonster (https://capmonster.cloud)

**Integration Flow (if implemented):**

1. **CAPTCHA Detected:**
    - Extract CAPTCHA image or reCAPTCHA site key
    - Send to third-party solver API
2. **Solver Processing:**
    - Service processes CAPTCHA (human solver or AI)
    - Returns solution token
    - Typical response time: 10-60 seconds
3. **Submit Solution:**
    - Submit solver token to Instagram/YouTube
    - Continue job execution if successful
4. **Cost Tracking:**
    - Log solver usage and cost per CAPTCHA
    - Display in analytics: "CAPTCHA solver used: 23 times (\$1.15)"

**Configuration:**

```json
{
  "captcha_solver": {
    "enabled": false,
    "provider": "2captcha",
    "api_key": "encrypted_key",
    "auto_solve": false,
    "max_cost_per_month": 50,
    "alert_on_usage": true
  }
}
```

**Note:** Third-party CAPTCHA solving is optional and requires separate subscription with providers. Implementation details will be provided in developer documentation.[^1]

***

## 5. User Interface Specifications

### 5.1 Screen Layouts and Navigation

**Main Navigation Menu (Sidebar):**

- 🏠 Dashboard
- 🔗 Connections
- 👤 Accounts
- 🌐 Proxies
- 📋 Jobs \& Logs
- 📊 Analytics
- 🔔 Notifications
- ⚙️ Settings


### 5.2 Detailed Screen Specifications

#### 5.2.1 Login Screen

**Layout:**

- Centered login card on branded background
- Fields: Username, Password
- Checkbox: Remember me
- Button: Login
- Password strength indicator on password field
- Error messages displayed below form


#### 5.2.2 Dashboard Screen

**Layout Sections:**

1. Top Banner: High-level metrics cards (4 columns)
2. Activity Feed (Left, 60%): Real-time job updates
3. Connection Status Grid (Right, 40%): Connection cards with quick actions
4. Bottom: Quick action buttons

**Responsive Design:**

- Desktop: Side-by-side layout
- Tablet: Stacked layout with full-width cards
- Mobile: Single column with collapsible sections


#### 5.2.3 Connections List Screen

**Layout:**

- Header: "Connections" + "Create New Connection" button
- Filter Bar: Status filter (All, Active, Paused, Stopped), Search box
- Connection Table/Cards:
    - Columns: Name, Type, Status, Source, Destination, Last Run, Success Rate, Actions
    - Actions: Start/Stop/Pause icons, View Details, Edit, Delete
- Pagination: 20 connections per page

**Connection Detail View (Modal or Separate Page):**

- Summary Section: Connection details, status, statistics
- Recent Jobs Table: Last 50 jobs with status
- Performance Chart: Success rate over time
- Action Buttons: Start/Stop/Pause, Run Now, Dry Run, Edit, Delete


#### 5.2.4 Connection Creation Wizard (Multi-Step Form)

**Step Indicator:** Progress bar showing current step (1/7)

**Step 1:** Basic Configuration
**Step 2:** Account Selection
**Step 3:** Proxy Configuration
**Step 4:** Filter Rules
**Step 5:** Scheduling
**Step 6:** Transform Options
**Step 7:** Review \& Save

**Navigation:** Back, Next, Cancel buttons on each step

#### 5.2.5 Accounts Management Screen

**Layout:**

- Tabs: Instagram Accounts | YouTube Accounts
- Header: "Add Account" button
- Account Cards Grid:
    - Each card shows: Alias, Username/Channel, Status indicator, Token expiry, Actions
    - Actions: Edit, View Analytics, Update Token, Delete

**Account Detail View:**

- Account Information section
- Token Status section with expiry countdown
- Connected Connections list
- Performance metrics
- Action buttons: Update Token, Re-authorize, Delete


#### 5.2.6 Proxy Management Screen

**Layout:**

- Header: "Add Proxy" button + "Test All" button
- Proxy Table:
    - Columns: Alias, Type, Host:Port, Status, Last Check, Latency, Actions
    - Status indicator: Green (healthy), Red (unhealthy), Gray (unchecked)
    - Actions: Test, Edit, Delete

**Add/Edit Proxy Form (Modal):**

- Fields: Alias, Type dropdown, Host, Port, Username, Password, Assignment radio buttons
- Buttons: Save \& Test, Save, Cancel


#### 5.2.7 Jobs \& Logs Screen

**Layout:**

- Tabs: Active Jobs | Job History | Dead-Letter Queue | Logs
- Filter Bar: Connection filter, Status filter, Date range picker, Search
- Jobs Table:
    - Columns: Job ID, Connection, Status, Source Post, Destination Post, Created, Duration, Actions
    - Status badges: Color-coded (green: success, red: failed, yellow: retrying, blue: running)
    - Actions: View Details, Retry (for failed), View Logs

**Job Detail View (Modal):**

- Job metadata
- Execution timeline with timestamps
- Error details if failed
- Retry history
- Related logs
- Action buttons: Retry, View Source, View Destination

**Logs Table:**

- Columns: Timestamp, Level, Job ID, Connection, Message, Actions
- Level badges: Info, Warning, Error, Critical
- Expandable message with full details


#### 5.2.8 Analytics Screen

**Layout:**

- Date Range Selector: Presets (Last 7 days, 30 days, 90 days) + Custom
- Tabs: Overview | Connections | Accounts | System
- Dashboard with multiple chart cards
- Export button (top-right)

**Charts:**

- Success Rate Trend (Line Chart)
- Job Volume by Day (Bar Chart)
- Failure Breakdown (Pie Chart)
- Top Connections Performance (Horizontal Bar Chart)
- Uptime Heat Map (Calendar View)


#### 5.2.9 Settings Screen

**Layout:**

- Tabs: Admin | Notifications | Retention | Retry Policy | Workers

**Admin Tab:**

- Change Password section
- Session timeout configuration

**Notifications Tab:**

- Telegram configuration form
- Test notification button
- Alert preferences checkboxes

**Retention Tab:**

- Log retention policy (days)
- Video retention policy (days)
- Cleanup schedule configuration

**Retry Policy Tab:**

- Global retry configuration
- Per-error-type settings

**Workers Tab:**

- Number of workers
- Queue priorities
- Worker health status

***

## 6. API Endpoints Specification

### 6.1 Authentication Endpoints

```
POST   /api/login                  - User login
POST   /api/logout                 - User logout
PUT    /api/admin/password         - Update admin password
GET    /api/auth/check             - Check session validity
```


### 6.2 Account Endpoints

```
GET    /api/accounts               - List all accounts
POST   /api/accounts               - Create new account
GET    /api/accounts/{id}          - Get account details
PUT    /api/accounts/{id}          - Update account
DELETE /api/accounts/{id}          - Delete account
POST   /api/accounts/{id}/captcha-resolve  - Mark CAPTCHA as solved
GET    /api/accounts/{id}/analytics         - Get account analytics
```


### 6.3 Connection Endpoints

```
GET    /api/connections            - List all connections
POST   /api/connections            - Create connection
GET    /api/connections/{id}       - Get connection details
PUT    /api/connections/{id}       - Update connection
DELETE /api/connections/{id}       - Delete connection
POST   /api/connections/{id}/start - Start connection
POST   /api/connections/{id}/stop  - Stop connection
POST   /api/connections/{id}/pause - Pause connection
POST   /api/connections/{id}/run   - Manual run now
POST   /api/connections/{id}/dry-run  - Test mode
```


### 6.4 Proxy Endpoints

```
GET    /api/proxies                - List all proxies
POST   /api/proxies                - Create proxy
GET    /api/proxies/{id}           - Get proxy details
PUT    /api/proxies/{id}           - Update proxy
DELETE /api/proxies/{id}           - Delete proxy
POST   /api/proxies/{id}/health-check  - Test proxy
POST   /api/proxies/test-all       - Test all proxies
```


### 6.5 Job \& Log Endpoints

```
GET    /api/jobs                   - List jobs (with filters)
GET    /api/jobs/{id}              - Get job details
POST   /api/jobs/{id}/retry        - Retry failed job
GET    /api/jobs/dead-letter       - List dead-letter queue
DELETE /api/jobs/{id}              - Delete job (dead-letter only)

GET    /api/logs                   - List logs (with filters)
GET    /api/logs/{id}              - Get log details
```


### 6.6 Token Endpoints

```
POST   /api/tokens/upload          - Upload token JSON (YouTube)
GET    /api/tokens/{id}/status     - Get token status and expiry
POST   /api/tokens/{id}/refresh    - Manually refresh token
```


### 6.7 Analytics Endpoints

```
GET    /api/analytics/summary?period=monthly    - System summary
GET    /api/analytics/connection/{id}/metrics   - Connection metrics
GET    /api/analytics/account/{id}/metrics      - Account metrics
POST   /api/analytics/export                    - Export analytics to CSV
```


### 6.8 Notification Endpoints

```
GET    /api/notifications          - List recent notifications
PUT    /api/settings/telegram      - Update Telegram config
POST   /api/settings/telegram/test - Send test notification
```


### 6.9 System Endpoints

```
GET    /api/health                 - System health check
GET    /api/dashboard/summary      - Dashboard summary data
GET    /api/settings               - Get system settings
PUT    /api/settings               - Update system settings
```



***
