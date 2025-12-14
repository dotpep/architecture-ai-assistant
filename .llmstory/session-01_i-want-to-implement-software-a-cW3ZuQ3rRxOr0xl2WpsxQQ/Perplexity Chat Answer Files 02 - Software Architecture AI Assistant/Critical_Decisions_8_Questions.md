# 🎯 CRITICAL DECISIONS & QUESTIONS - Before Implementation

## Your Project Context

**Project**: Software Architecture AI Assistant (Diagram Generator)
**Course**: Cloud-Native AI Application Deployment (Final Project)
**Goal**: Strong Cloud Infrastructure + Simple Working AI App
**Constraint**: AWS Free Tier, No Auth/Payment, MVP Only

---

## ⚠️ ANALYSIS OF YOUR SYSTEM THOUGHTS

### ✅ What You Got Right:
1. **Infrastructure-first mindset** - Good! Cloud architecture matters more than features
2. **Microservices backend** - Smart for cloud deployment
3. **Monolith frontend** - Correct for simplicity
4. **PlantUML/diagram generation** - Good choice for architecture diagrams
5. **DynamoDB for chat history** - Perfect for serverless
6. **S3 for diagram storage** - Standard approach

### ⚠️ Areas Needing Clarification:
1. **Lambda vs K8s debate** - Depends on your priorities
2. **Frontend hosting location** - Not specified
3. **PlantUML vs Mermaid** - Different use cases
4. **Real-time requirements** - Affects architecture significantly
5. **Project/folder feature** - Adds complexity
6. **Canvas vs Image display** - Different technical approaches
7. **Code generation showing** - Affects UX significantly
8. **S3 necessity** - May be overkill for MVP

---

# 📋 8 CRITICAL QUESTIONS YOU MUST ANSWER

## Question 1: COMPUTE STRATEGY
### Lambda vs ECS (Containers + K8s) - Which is Better for YOUR Case?

**The Debate:**

```
LAMBDA APPROACH:
✅ Pros:
  - Zero infrastructure management
  - Auto-scaling built-in
  - Pay per invocation (AWS free tier covers it)
  - Easier Terraform
  - Faster deployment
  - Perfect for stateless workloads

❌ Cons:
  - Max 15-minute execution (PlantUML might timeout)
  - Cold starts (first request slow)
  - Limited customization
  - Doesn't showcase K8s skills

ECS + FARGATE APPROACH:
✅ Pros:
  - No cold starts
  - Custom Docker images
  - Better for long-running tasks
  - Shows container knowledge
  - Perfect for PlantUML server
  - Easier troubleshooting

❌ Cons:
  - Requires Docker container management
  - More infrastructure code
  - More complexity for MVP
  - Costs more on free tier

EKS (KUBERNETES) APPROACH:
✅ Pros:
  - Industry standard (best for portfolio)
  - K8s manifests required for course
  - Great learning opportunity
  - Scalable

❌ Cons:
  - **NOT FREE TIER FRIENDLY** ($0.10/hour minimum)
  - Way too complex for MVP
  - Overkill for this project
```

**Your Decision Needed:**
```
☐ Lambda-only (simplest, fastest)
☐ ECS Fargate (balanced, good learning)
☐ EKS (overkill, not recommended)
```

---

## Question 2: FRONTEND HOSTING
### Where Should Your Monolith Frontend Live?

**Your Options:**

```
OPTION A: S3 + CloudFront (RECOMMENDED FOR MVP)
├─ Static React app hosted on S3
├─ CloudFront for CDN & HTTPS
├─ 100% within free tier
├─ Fast, simple
└─ Cost: ~$0

OPTION B: EC2 (Simple but Wastes Resources)
├─ Single t2.micro instance
├─ Run Next.js server
├─ Full control
└─ Cost: ~$0 (free tier) or ~$10/month after

OPTION C: App Runner (Middle Ground)
├─ Container registry + managed service
├─ Easier than ECS
├─ Still within free tier for small app
└─ Cost: ~$0-5/month

OPTION D: ECS + Load Balancer
├─ Full microservices stack
├─ Overly complex for MVP
└─ Cost: More expensive
```

**Your Decision Needed:**
```
☐ S3 + CloudFront (best for this project)
☐ EC2 (simple but less cloud-native)
☐ App Runner (good learning)
☐ ECS (too complex)
```

---

## Question 3: DIAGRAM RENDERING
### PlantUML vs Mermaid vs React Flow?

**Comparison Table:**

```
┌─────────────┬─────────────────┬─────────────────┬──────────────┐
│ Feature     │ PlantUML        │ Mermaid         │ React Flow   │
├─────────────┼─────────────────┼─────────────────┼──────────────┤
│ Learning    │ Text-based code │ Text-based code │ JavaScript   │
│ Curve       │ (Steep)         │ (Easy)          │ (Medium)     │
├─────────────┼─────────────────┼─────────────────┼──────────────┤
│ Diagram     │ ✓ C4            │ ✓ Flowchart     │ ✓ Custom     │
│ Types       │ ✓ ER            │ ✓ Sequence      │ ✓ Mermaid    │
│             │ ✓ Sequence      │ ✓ ER            │ ✓ State      │
│             │ ✓ State         │ ✓ Gantt         │ ✗ C4         │
├─────────────┼─────────────────┼─────────────────┼──────────────┤
│ Setup       │ Docker image    │ npm package     │ npm package  │
│ Complexity  │ (Medium)        │ (Easy)          │ (Easy)       │
├─────────────┼─────────────────┼─────────────────┼──────────────┤
│ Output      │ Image (PNG/SVG) │ Image (PNG/SVG) │ SVG/Canvas   │
│             │ needs server    │ client-side     │ client-side  │
├─────────────┼─────────────────┼─────────────────┼──────────────┤
│ Free Tier   │ ✓ Docker        │ ✓ Free          │ ✓ Free       │
│ Cost        │ Container       │ JavaScript      │ JavaScript   │
└─────────────┴─────────────────┴─────────────────┴──────────────┘

HYBRID APPROACH (BEST FOR YOUR PROJECT):
├─ Mermaid for code generation from AI
│  (simple, text-based, easy to parse)
├─ React Flow for interactive canvas
│  (editable, shows live updates)
└─ Both as outputs (markdown + interactive)
```

**Your Decision Needed:**
```
☐ PlantUML (if supporting C4 diagrams is critical)
☐ Mermaid (simpler, recommended)
☐ React Flow (interactive, best UX)
☐ Hybrid: Mermaid + React Flow (BEST OPTION)
```

---

## Question 4: DISPLAY METHOD
### Canvas/Interactive vs Static Images?

**The Trade-off:**

```
STATIC IMAGE APPROACH (SIMPLER):
├─ AI generates PlantUML/Mermaid code
├─ Backend renders to PNG/SVG image
├─ Frontend shows <img src="..."
├─ Implementation time: 2-3 days
├─ Complexity: Low
└─ User sees: Final result only

INTERACTIVE CANVAS (BETTER UX):
├─ AI generates PlantUML/Mermaid code
├─ Frontend parses code into JSON
├─ React Flow renders interactive diagram
├─ Users can zoom, pan, drag
├─ Implementation time: 4-5 days
├─ Complexity: Medium
└─ User sees: Live interactive canvas

HYBRID (BEST):
├─ Show Mermaid code in chat (real-time)
├─ Show rendered image (instant)
├─ Show interactive canvas below (editable)
└─ Implementation time: 5-6 days
```

**MVP REALITY CHECK:**
```
For a final project with:
- Limited time (9 weeks)
- Focus on INFRASTRUCTURE (not features)
- Simple working app

RECOMMENDATION: Static images + optional interactive later
This lets you focus 80% effort on cloud infrastructure
and 20% on app features.
```

**Your Decision Needed:**
```
☐ Static images only (fastest)
☐ Interactive canvas (better UX)
☐ Both (if time permits)
```

---

## Question 5: REAL-TIME DIAGRAM GENERATION
### Show Code Generation in Real-Time or Final Result Only?

**Scenario A: Real-Time Updates (Complex)**
```
User: "Create C4 diagram for microservices"
     ↓ (2-3 seconds)
AI: "```mermaid\ngraph TD\n  A[User]"
     ↓ (streaming real-time)
Frontend: Shows updating code as it generates
     ↓ (5 seconds)
AI: "```mermaid\ngraph TD\n A[User] → B[API Gateway]...\n```"
     ↓
Final diagram rendered
```

**Problems:**
- Adds WebSocket complexity
- Requires streaming LLM response
- More expensive (CloudWatch logs)
- Plus rendering updates on frontend
- Not free tier friendly

**Scenario B: Final Result Only (Simple)**
```
User: "Create C4 diagram for microservices"
     ↓ (3-5 seconds)
AI: Generates complete code
     ↓
Backend: Renders to image
     ↓
Frontend: Shows final diagram
```

**Benefits:**
- Simple implementation
- Works within free tier
- Faster development
- Good enough for MVP

**Your Decision Needed:**
```
☐ Real-time code updates (complex, fancy)
☐ Final result only (simple, sufficient)
```

**My Recommendation**: Final result only. You have 9 weeks. Spend time on cloud infrastructure.

---

## Question 6: PROJECT/FOLDER FEATURE
### Do You REALLY Need Project Organization?

**What This Means:**
```
WITHOUT Projects:
├─ User logs in (no auth, so just session)
├─ Can create unlimited diagrams
├─ All diagrams listed in one page
├─ Search/filter diagrams
└─ Complexity: Low ✓

WITH Projects:
├─ User creates a "Project" (like folder)
├─ Inside project, create multiple diagrams
├─ Organize by project
├─ Share entire projects
├─ Complexity: Medium ✗
└─ Database design: More complex

DATABASE IMPACT:
Without Projects:
  ├─ User table
  ├─ Chat table (userId, message, timestamp)
  ├─ Diagram table (userId, diagramCode, type)
  └─ Total: 3 tables

With Projects:
  ├─ User table
  ├─ Project table (userId, projectName)
  ├─ Chat table (userId, projectId, message)
  ├─ Diagram table (userId, projectId, code)
  └─ Total: 4 tables + relationships
```

**Extra Complexity Added:**
- Frontend: Project navigation UI
- Backend: Project CRUD endpoints
- Database: Relationships & queries
- Time cost: +3-4 days

**MVP Question**: Do you REALLY need this for final project evaluation?

**Your Decision Needed:**
```
☐ Yes, include projects (organization matters to me)
☐ No, skip projects (simpler MVP, better infrastructure focus)
```

**My Recommendation**: Skip for MVP. Add later if time permits.

---

## Question 7: AUTHENTICATION & AUTHORIZATION
### Do You Need User Auth or Can You Skip It?

**Current State:**
```
Your note: "We don't need Auth and Authorization"

But check course requirements:
- Does professor expect login? 
- Do requirements mention user management?
- Are you storing PER-USER data?
```

**Two Approaches:**

```
APPROACH A: NO AUTH (Stateless)
├─ No user login needed
├─ Session-based using browser cookies
├─ DynamoDB stores by sessionId
├─ Any user can access any diagram
├─ Complexity: Very Low ✓
└─ Time: 0 days

APPROACH B: SIMPLE AUTH (AWS Cognito)
├─ AWS Cognito free tier
├─ Email + password sign-up
├─ Basic user isolation
├─ Each user sees only their diagrams
├─ Complexity: Low ✓✓
└─ Time: 2-3 days

APPROACH C: COMPLEX AUTH
├─ Custom JWT implementation
├─ OAuth integration
├─ Role-based access
└─ SKIP THIS (not MVP)
```

**Reality Check for YOUR Project:**
- This is a final project (small scale)
- No real users will use it
- Evaluation is on cloud infrastructure + AI integration
- Auth adds NO value to evaluation

**Your Decision Needed:**
```
☐ No auth (anonymous/session-based) - RECOMMENDED
☐ Simple Cognito auth
☐ Don't know yet (will check requirements)
```

**My Recommendation**: Session-based only. Use browser sessionId or simple token.

---

## Question 8: S3 FOR IMAGE STORAGE
### Is S3 Really Necessary, or Overkill?

**Your Needs Analysis:**

```
DO YOU NEED S3 IF:
✓ Users download diagrams later → YES
✓ Users want to store diagram history → YES  
✓ You need to serve images fast → MAYBE (CloudFront)
✓ You want to keep diagrams long-term → YES

DO YOU NOT NEED S3 IF:
✗ Diagrams are temporary (generated on request)
✗ No download feature
✗ Users don't need to revisit old diagrams
✗ You only show current generated diagram
```

**Two Approaches:**

```
APPROACH A: ON-DEMAND RENDERING (NO S3 NEEDED)
├─ User requests diagram
├─ Backend generates from stored Mermaid code
├─ Render to PNG on the fly
├─ Show in frontend
├─ Delete after session ends
├─ Complexity: Low
├─ Storage: DynamoDB only (code, not images)
├─ Cost: Cheap
└─ Upside: Cleaner, simpler, MVP-ready

APPROACH B: STORE IN S3 (GOOD PRACTICE)
├─ Generate diagram
├─ Save code to DynamoDB
├─ Save image to S3
├─ Users can download/share
├─ Can list all generated diagrams
├─ Complexity: Medium
├─ Storage: DynamoDB + S3
├─ Cost: Minimal (free tier covers)
└─ Upside: Shows S3 knowledge, better UX
```

**Your Course Requirement Check:**
```
Project says: "4 different cloud services integrated"

Currently planning:
1. API Gateway ✓
2. Lambda ✓
3. DynamoDB ✓
4. ??? (S3? CloudFront? SNS?)

If you skip S3, you might not hit "4 services" requirement.
```

**Your Decision Needed:**
```
☐ Skip S3 (keep images in memory/DynamoDB)
☐ Use S3 (better for portfolio, hits 4-service requirement)
☐ Check course requirements first
```

**My Recommendation**: Use S3 for diagram images. It's a standard practice and helps meet the "4 services" requirement.

---

# 📊 DECISION MATRIX - What To Choose

Based on your goal: **"Strong Cloud Infrastructure + Simple Working App"**

```
INFRASTRUCTURE FOCUS ✓✓✓:
┌─────────────────────────────────────────┐
│ Compute:     Lambda (simple) OR          │
│              ECS Fargate (better)        │
│                                          │
│ Frontend:    S3 + CloudFront             │
│                                          │
│ Database:    DynamoDB (chats + diagrams) │
│                                          │
│ Storage:     S3 (diagram images)         │
│                                          │
│ Optional:    API Gateway, CloudWatch     │
└─────────────────────────────────────────┘

APP SIMPLICITY ✓✓:
├─ Mermaid + React Flow (for diagrams)
├─ No real-time streaming
├─ Final result only
├─ No projects (just list diagrams)
├─ Session-based (no Auth)
└─ Static display first, interactive later

TOTAL SERVICES: 4-5
├─ API Gateway (routing)
├─ Lambda/ECS (compute)
├─ DynamoDB (database)
├─ S3 (storage)
└─ CloudFront (CDN)
```

---

# 🎯 NEXT STEPS

## Once You Answer These 8 Questions:

1. **Question 1**: Lambda vs ECS → Affects all infrastructure
2. **Question 2**: Frontend hosting → S3+CloudFront or EC2
3. **Question 3**: Diagram tech → Mermaid vs React Flow
4. **Question 4**: Display type → Static vs Interactive
5. **Question 5**: Real-time → Stream or final only
6. **Question 6**: Projects → Include or skip
7. **Question 7**: Auth → None, Session, or Cognito
8. **Question 8**: S3 → Include or skip

## Then We Will:

1. ✅ Create detailed architecture diagram (Mermaid/PlantUML)
2. ✅ Design Terraform infrastructure code structure
3. ✅ Create comprehensive spec document
4. ✅ Prepare for Claude Sonnet agentic coding
5. ✅ Generate complete implementation guide

---

# ⏱️ TIMELINE IMPACT

```
Without Projects, Real-time, Auth:
├─ Infrastructure setup:  2-3 days
├─ Backend (Lambda/API):  2-3 days
├─ Frontend (React):      2-3 days
├─ Integration:           2-3 days
├─ Testing & Deploy:      1-2 days
└─ Total: 10-15 days ✓ (good for 9 weeks)

With Projects, Real-time, Auth:
├─ Infrastructure setup:  2-3 days
├─ Backend (complexity):  4-5 days
├─ Frontend (complexity): 3-4 days
├─ Integration:           2-3 days
├─ Testing & Deploy:      1-2 days
└─ Total: 15-20 days ⚠️ (tight for 9 weeks)
```

---

## 📝 PLEASE ANSWER THESE 8 QUESTIONS:

**Copy and paste this, fill in your answers:**

```
1. Compute Strategy:      ☐ Lambda  ☐ ECS Fargate  ☐ EKS
2. Frontend Hosting:      ☐ S3+CF   ☐ EC2         ☐ AppRunner
3. Diagram Tech:          ☐ PlantUML ☐ Mermaid    ☐ Hybrid
4. Display Method:        ☐ Static  ☐ Interactive ☐ Both
5. Real-time Generation:  ☐ Yes     ☐ No
6. Project Folders:       ☐ Yes     ☐ No
7. Authentication:        ☐ None    ☐ Session     ☐ Cognito
8. S3 Storage:            ☐ Yes     ☐ No

Additional Context (if needed):
- Course requirements about auth?
- Professor expects specific tech?
- Timeline pressure level?
- Learning goals (infrastructure vs features)?
```

---

**Once you provide these answers, I'll give you:**

✅ Optimized system architecture diagram (Mermaid)
✅ Terraform code structure plan
✅ API specifications
✅ Database schema
✅ Implementation guide for Claude Sonnet agentic coding
✅ Complete specification-driven development document

**Then we'll proceed to the "Claude Sonnet agent" phase for code generation!**

---

**Version**: 1.0
**Date**: December 14, 2025
**Status**: Awaiting Your Decisions
