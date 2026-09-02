# RETROSPECTIVE

Last updated: 2026-09-02

## What Went Well

- Public repository baseline documents (README, CONTRIBUTING, CODE_OF_CONDUCT, LICENSE) were already in place.
- Existing CI/CD workflows reduced setup time and allowed incremental hardening instead of rebuilding from scratch.
- Feature flag and experiment artifacts made it easy to justify Persevere decision with evidence.

## What Was Improved

- Added deployable AI API endpoint and metrics endpoint for operational readiness.
- Added explicit rollback steps in runbook.
- Connected local observability stack to the API service.
- Added mini eval job to strengthen PR gate confidence.
- Built the iPad demo from setup through PencilKit drawing, on-device analysis, emotion exhibition, 3D RGB distribution, and local archive.
- Integrated a 10-family emotion classification layer while keeping the network overlay optional for visual clarity.
- Separated the product analysis path (Swift on-device), deployable API prototype (Node heuristic), and research validation path (Python).

## What Was Hard

- Aligning mixed runtime components (Python analysis artifacts + Node package/workflows).
- Ensuring deliverables are both technically present and submission-readable.
- Keeping product documents synchronized while the implementation moved from an API-first plan to an on-device-first iPad prototype.

## Next Iteration

1. Add corrected emotion and note feedback, then apply it to the personal distribution model.
2. Add color wheel, HEX/RGB input, eyedropper, and reusable palettes.
3. Add Swift tests and a real-device regression checklist for the complete drawing-to-archive flow.
4. Decide the on-device/remote analysis boundary before adding authentication, synchronization, and database storage.
5. Validate the iPhone viewing companion after the paid iPad experience is stable.
