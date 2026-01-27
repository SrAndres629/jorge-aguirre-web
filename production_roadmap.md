# Production Roadmap: Natalia Core v3.1

Goal: Achieve a 100% stable, self-recovering, and high-conversion AI Sales system.

## Phase 1: Stabilization (DONE)
- [x] Gemini AI Cognitive Engine verified.
- [x] Infrastructure Guardian CLI (`render_manager.py`) stabilized.
- [x] Evolution API (The Body) joined with NataliaBrain (The Mind).

## Phase 2: Refinement (CURRENT)
- [ ] **Log Analysis**: Verify startup messages and cognitive traces in production.
- [ ] **Zero-Technical-Debt Check**: Audit `natalia-brain` codebase for hardcoded values.
- [ ] **Human-in-the-Loop Verification**: Final admin test message response.

## Phase 3: Scaling & ROI (NEXT)
- [ ] **Lead Scoring**: Activate automatic metadata extraction for client segmentation.
- [ ] **Meta CAPI**: Verify event firing for conversion tracking.
- [ ] **Growth**: Deployment of "Chief Consultation" module for high-ticket closing.

## Maintenance Protocol
1. Daily health check via `python render_manager.py --audit`.
2. Automatic recovery via `restore_env.py` if Render keys rotate.
3. Proactive updates via `git_sync.py`.
