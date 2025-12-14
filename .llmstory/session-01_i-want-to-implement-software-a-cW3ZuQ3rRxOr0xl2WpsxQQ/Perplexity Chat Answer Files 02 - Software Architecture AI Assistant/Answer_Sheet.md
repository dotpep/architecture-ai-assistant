# ANSWER SHEET - Your 8 Critical Decisions

**Please fill this out and provide your answers!**

---

## YOUR ANSWERS

### 1️⃣ COMPUTE STRATEGY - Which Approach?
**Question**: How should backend services run?

- [x] **Lambda** (serverless, simplest, free tier friendly)
- [ ] **ECS Fargate** (containerized, better for PlantUML, more control)
- [ ] **EKS** (Kubernetes, NOT RECOMMENDED - too complex, not free)

**Why This Matters:**
- Lambda: 0-5 days setup, simple Terraform
- ECS: 5-7 days setup, Docker required
- EKS: 7-10 days setup, overkill for MVP

**Your Choice**: for backend is lambda, and we need to make it modular and simple!!!

---

### 2️⃣ FRONTEND HOSTING - Where Does React App Run?

- [x] **S3 + CloudFront** (RECOMMENDED - static site hosting, fast, free)
- [ ] **EC2** (traditional server, wastes resources for static site)
- [ ] **App Runner** (managed service, between S3 and EC2)
- [ ] **ECS** (same as backend, overkill for static frontend)

**Why This Matters:**
- S3+CF: ~$0/month, fastest deployment
- EC2: ~$0/month (free tier) or $10/month after
- App Runner: ~$5/month minimum
- ECS: ~$20+/month minimum

**Your Choice**: s3+cf, we need make it simpler!!! and also we have SPA, only the chat page, where user can only chat with llm to generate the Diagrams

---

### 3️⃣ DIAGRAM TECHNOLOGY - How to Generate & Render Diagrams?

- [ ] **PlantUML** (text-based, C4 diagrams, requires server for rendering)
- [ ] **Mermaid** (text-based, easier, client-side rendering)
- [ ] **React Flow** (visual/interactive, client-side rendering)
- [x] **Mermaid + React Flow Hybrid** (RECOMMENDED - best UX + simplicity)

**Diagram Types Needed:**
- C4 diagrams: Better with PlantUML
- Flowcharts, Sequence, ERD: Better with Mermaid
- Interactive editing: Better with React Flow

**Your Choice**: Mermaid + React Flow Hybrid, if the Cloude Sonet OPUS 4.5 is capable to do it, then why not, but if this causes an errors and i will have a troubles, i will re chose to the Mermaid ony approach (we dont want to debug the AI Application, we need to concentrate on Deployment and Infrastructure) (it is nice to have and we will try it to implement)

**Follow-up**: Which diagram types do you absolutely need for MVP?
- [ ] C4 Architecture
- [ ] Entity-Relationship (ERD)
- [ ] Sequence Diagrams
- [ ] Data Flow Diagrams
- [ ] Flowcharts
- [ ] RBAC Matrix

**Your Answer**: All types diagrams!!! as much possible as we need to do so, (if mermaid cannot generate the c4 diagram, then we need just the High level diagram, overview of system like diagram), and also (if like matrix is not supported then let it go!!!) (also we can additional of types of diagrams) (we would have the simple feature of choosing the most popular 4-6 diagram types to generate in our LLM chat and Architect AI Assistant, and one of the default: called like Project (come up with good naming) that will generate all types of Diagrams listed in the Diagram types list/dropdown (but if it adds the additional layer of complexity, we would also skip this part!!! it is nice to have and we will try it to implement)) (we need to provide)

---

### 4️⃣ DISPLAY METHOD - How Should Diagrams Appear?

- [ ] **Static Images Only** (PNG/SVG shown as `<img>`, simplest, fastest)
- [ ] **Interactive Canvas** (React Flow with zoom/pan/drag, better UX)
- [x] **Both** (code preview + static image + interactive, if time permits)

**Time Impact:**
- Static only: 2-3 days
- Interactive: 4-5 days
- Both: 6-7 days

**Your Choice**: Both, but it is also nice to have (if bugs occur then we would skip it)

---

### 5️⃣ REAL-TIME CODE GENERATION - Show Live Updates?

- [ ] **Yes** (stream code as AI generates, fancy but complex)
- [x] **No** (show final diagram only, simple and sufficient)

**Why This Matters:**
- Real-time: Requires WebSocket, streaming LLM, more infrastructure
- Final only: Simple polling, standard architecture

**Complexity Cost**: +2-3 days if "Yes"

**Your Choice**: no we dont need the real time!!! final result only!!!

**If "Yes" - Why**: What's the learning value for you?
_______________

---

### 6️⃣ PROJECT ORGANIZATION - Do You Need Folders?

- [ ] **Yes** (organize diagrams into projects/folders)
- [x] **No** (simple flat list, just search/filter diagrams)

**What This Adds:**
- Yes: Project CRUD, more DB queries, UI navigation
- No: Simple table, all diagrams in one view

**Database Complexity:**
- No: 3 tables (Users, Chats, Diagrams)
- Yes: 4+ tables with relationships

**Your Choice**: no, we dont need the projects!!! we will implement just the simple, and usual/standard chat!

**If "Yes" - Why**: Is this required by your professor?
_______________

---

### 7️⃣ USER AUTHENTICATION - How to Identify Users?

- [x] **No Auth** (session-based using sessionId, anonymous/guest)
- [ ] **Simple Auth** (AWS Cognito or basic email/password)
- [ ] **JWT Auth** (custom authentication, more complex)

**Why This Matters:**
- No Auth: 0 days setup, works for MVP
- Simple: 2-3 days setup with Cognito
- Custom JWT: 4-5 days setup

**Your Choice**: No!!! we will not do and implement the authentication! (we need to make our app, as simpler as much!!!) (save the chats just for the one user!!!, and do not implement any logic of it!, because we will showcase/demo the project and that's it, it is not the production or any like this!!!, only the me will use this app!)

**Course Requirement Check:**
Does your professor require authentication?
- [ ] Yes, explicitly mentioned
- [x] No, not mentioned
- [ ] Don't know / Not sure

**Your Choice**: no, our proffessor not required the authentication!!!

---

### 8️⃣ IMAGE STORAGE - Should You Use S3?

- [x] **Yes, Use S3** (store diagram images, standard practice, hits 4-service requirement)
- [ ] **No, Skip S3** (generate images on-demand, keep code in DynamoDB)

**Why This Matters:**
- With S3: Better UX (download, share), shows best practices, fulfills "4 services"
- Without S3: Simpler, faster to implement, still works

**Your Choice**: yes we need to store the generated Mermaid text/code and also in the image formats of diagrams into S3

**Follow-up**: Does your project requirement mention "4 different cloud services"?
- [x] Yes, explicitly
- [ ] Yes, but unclear
- [ ] No, not mentioned

**Your Answer**: Yes, we need the s3!!!

---

# 📊 ADDITIONAL CONTEXT QUESTIONS

### ❓ Course Requirements Clarity

**Q1**: Does your professor REQUIRE authentication?
- [ ] Explicitly required
- [ ] Suggested but optional
- [ ] Not mentioned
- [ ] Will check
- [x] No required

**Q2**: Do you need to hit "4 different cloud services" requirement?
- [x] Yes, explicitly stated
- [ ] Probably (to be safe)
- [ ] No, not required
- [ ] Don't know

**Q3**: Is Kubernetes/EKS mentioned as a requirement?
- [ ] Yes, required
- [x] Mentioned as option
- [ ] Not mentioned
- [ ] Don't know

**Q4**: Does the project require "live deployment & accessible URL"?
- [x] Yes
- [ ] Probably
- [ ] Not sure

---

### ⏱️ Your Timeline & Priorities

**Q5**: How much time do you realistically have?
- [ ] 3 weeks
- [ ] 6 weeks
- [ ] 9 weeks (full semester)
- [ ] Other: 2 days (16 hours or less)

**Q6**: What matters more to you for evaluation?
- [x] Infrastructure/Cloud Architecture (80%)
- [ ] Balanced (50/50) Infrastructure + Features
- [ ] Features/AI Integration (80%)

**Your Answer**: Infrastructure/Cloud Architecture

**Q7**: What's your skill level with:
- AWS: [ ] Beginner  [x] Intermediate  [ ] Expert
- Terraform: [x] Beginner  [ ] Intermediate  [ ] Expert
- React: [ ] Beginner  [x] Intermediate  [ ] Expert
- Docker: [ ] Beginner  [x] Intermediate  [ ] Expert
- LLM APIs: [ ] Beginner  [x] Intermediate  [ ] Expert

---

### 🎯 Learning Goals

**Q8**: What do you want to learn most from this project?
- [x] Terraform & Infrastructure-as-Code
- [x] AWS cloud services
- [ ] Microservices architecture
- [ ] AI/LLM integration
- [ ] Full-stack development
- [ ] All of the above

---

# 📋 SUMMARY FOR ME

Once you answer all questions above, provide this summary:

```
CHOSEN ARCHITECTURE:
├─ Compute: lambda
├─ Frontend: s3+cloudfront
├─ Diagrams: mermaid+react flow
├─ Display: hybrid
├─ Real-time: no
├─ Projects: no
├─ Auth: no
└─ S3: yes

TIMELINE: 16 hours and less available

PRIORITY: infrastructure (infrastructure vs features)

KEY CONSTRAINT: using IaC terraform, and easy deploy with like one command (and also in the setup)

LEARNING GOAL: deployment of aws cloud native ai application
```

---

# 🚀 WHAT HAPPENS NEXT

**After you provide your answers:**

1. ✅ I'll validate your architecture choices
2. ✅ Create detailed architecture diagram (Mermaid)
3. ✅ Design Terraform code structure
4. ✅ Write API specifications
5. ✅ Create database schema
6. ✅ Generate implementation guide
7. ✅ Prepare for Claude Sonnet agentic coding

**Then we'll have:**
- Complete system design
- Terraform templates
- Implementation specifications
- Ready for Claude agent to code

---

**Ready?** 

Please fill out this form and send me your answers!

After that, we proceed with:
- Detailed architecture diagrams (Mermaid/PlantUML)
- Terraform code structure
- API & database specs
- Claude Sonnet agentic coding setup

---

**Version**: 1.0
**Date**: December 14, 2025
**Status**: Awaiting Your Answers
