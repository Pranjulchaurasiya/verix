# Verix scan integration

The scan-mode selector defaults to an explicitly simulated demo. Examples always use deterministic demo evidence. Connected API mode posts multipart `url` or `file`, plus `persona_mode`, to `/api/v1/analyze`. Set `NEXT_PUBLIC_API_BASE_URL` to the FastAPI origin for separate hosting; configure backend CORS for the frontend origin. No API secrets belong in public environment variables.

Demo mode rejects arbitrary pasted URLs and uploaded images rather than inventing results; only the explicit sample investigation buttons use mock scenarios.

`lib/scan-service.ts` owns requests, a 60-second timeout, errors and defensive mapping of `ScanResponse`. Failures do not silently become demo verdicts. Connected results expose explicit provenance: `live_serpapi`, `cached`, or `development_fallback`; demo fixtures remain client-side simulated data. Trusted platforms are source signals, but they no longer skip multi-source image analysis.

History remains behind `lib/history-store.ts`, with device-local persistence. Backend history synchronization is not implemented. Uploads and scan records are also stored by FastAPI; automatic deletion is not guaranteed.

Connected analyze and history service requests use `lib/client-scope.ts`: a random UUID persisted as `verix_client_id` is sent through `X-Client-Id`. The identifier is never included in UI, reports or logs. Storage failures stop connected requests with a recovery message; demo mode does not create an identifier. Clearing browser storage loses access to that anonymous backend history. Configure CORS to permit `X-Client-Id`. `fetchScanHistory` and `fetchScanById` provide scoped retrieval; wiring them into the local history UI remains separate work.

Evidence export downloads JSON including the displayed result, image, timestamps, URLs, prices, confidence, recommendations and limitations. Printing/PDF generation is not implemented. Demo URLs use reserved .example domains in the main sneaker scenario and are illustrative, not findings about actual merchants.

Build verification requires completing the existing dependency install. The current environment contains partially installed Next and icon packages; missing declarations prevent a clean type check. Browser QA and real API end-to-end testing remain outstanding.
