# Final actual-export review — Understand spending EN v1

Four finished MP4 files: 27.100 seconds each, 813 frames, 30 fps, H.264 High/yuv420p/BT.709, AAC stereo 48 kHz. Landscape 1920×1080; portrait 1080×1920. This review binds to the exact SHA-256 values below. The films are local; this agent has not changed the app, website, Git or publication state.

| Actual export | SHA-256 |
|---|---|
| landscape / abgehakt-store.mp4 | 177f4eb7788b32d22c777c484b3437c2b379a6f47f100121135121e920a2b1c8 |
| landscape / abgehakt.mp4 | d36c4bbbfd031e197e8a5fd92a3a0f33dd50c8a45b0e5207476dea2f3e122be5 |
| portrait / abgehakt-store.mp4 | be9fb0e6d987d8a71f2fdce27e68d522a0936f03dccae63865d38dd9feb4ecee |
| portrait / abgehakt.mp4 | 8d618f0c2177d962f1b762d7a6e4200ec2311000c847a636b27ef7f14efdc4b1 |

Executed checks: complete FFmpeg decode of all four final MP4s; FFprobe metadata; no detected black-frame runs; identical AAC payload in all four; 13 actual midpoint states per format compared with the correct source compositions; every cut checked one frame before and on the cut; final frame checked; all 7 app shots per format retain the complete proportional English source screen and match their newly measured focus; all 5 photo shots per format fill every edge. The before/after cut frames, actual midpoint sheets and final frames are retained under review/ and portrait/review/.

Measured audio in every final encoded file: −18.0 LUFS integrated, 2.2 LU loudness range, oversampled true peak −2.6 dBTP. A fixed gain preserves the native takes while retaining peak headroom; the approximate −16 LUFS production target was limited by that peak reserve. There is no time stretching: Jessica eleven_v3 speed 1.0 throughout. Three valid Jessica clips are reused and four are newly generated. Independent ASR confirms their text; narration and on-screen text preserve the same claims. The maximum word-to-word gap is 1.22 s and retains the price-detail result followed by the short Pro-context photo; no empty slate was inserted.

Subtitles: 9 English cues per format; every actual burned-cue bounding box measured inside its safe zone, outside the complete app image. VTT, ASS and narration punctuation agree. Closing sentence is split into its natural three caption phrases.

Visual and product review: actual encoded midpoint sheets for both formats, a 360px portrait sheet, the exact English capture sources and whole-photo edges were viewed. Both monthly cards remain €359.90/10 purchases and €405.08/13 purchases. Price history remains a record of entered prices. The top-three item focus encloses Coffee, Salmon fillet and Milk by spending amount. The store focus encloses both real store rows and bars. Categories, item ranking and store breakdown carry Pro version labels; months and basic price history carry Free labels. No German count labels remain in the final source captures.

The 14 skill perspectives were covered by one agent: production scope, product/facts, marketing and first-user clarity, story order, English editing, brand/art direction, photograph continuity, complete UI capture, cuts/highlights, speaker direction, music, accessibility/store communication, technical QA and critical review. Speech warmth, emotion, pronunciation quality and music groove are not confirmed by ASR or meters. No actual subjective listening or real-time audiovisual playback was performed; the visual review used actual decoded frames. No audience study or independent expert panel is claimed.

| Finding | Status | Evidence / resolution |
|---|---|---|
| C01 store wording | Closed | Exact narration/CC: “Compare your spending by store.”; matching real SPENDING BY STORE section. |
| C02 English focus geometry | Closed | New EN semantic/pixel evidence in focus-source.json; section top moved to y336 where EN nodes require it. Final transformed rectangles pass. |
| C03 entered-price limitation | Closed | “prices you’ve recorded” and cost note “Based on your saved prices”; no automatic retailer search claim. |
| C04 Free/Pro boundary | Closed | Free labels for base screens; Pro version spoken at transition and displayed on all three advanced screens. |
| C05 native timing | Closed | 27.1s final duration from complete natural takes, no speedup, retained price row→detail and closing wide/detail/brand states. |
| F01 isolated subtitle words (P2) | Closed | Actual first export showed “off.”/“budget.” alone. Final files use balanced “things off.”/“your budget.”; re-encoded burned files then fully revalidated. |
| F02 untranslated purchase counts (P1) | Closed before final render | Early genuine UI capture showed Einkäufe. Root corrected the actual localized app output; final semantic nodes and viewed exports say purchases. No screenshot repaint. |
| L01 subjective audio review | Not checked | Hearing unavailable; exact technical measurements and independent ASR are retained without a claim about subjective vocal or musical quality. |

No open observed P0/P1 finding remains in the checks performed. Publication/integration belongs to root’s distribution step.
