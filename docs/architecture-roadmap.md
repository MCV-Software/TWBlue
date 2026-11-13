# Incremental architecture roadmap

Initial audit: 2026-11-13, baseline `003907ed`. Progress reviewed through `e091155b`.

## Objective and boundaries

Migrate incrementally with three layers: **views**, **controllers**, and **sessions/model**. Formatting helpers belong alongside controllers; relationship and collection policies belong alongside sessions. There are no additional top-level domain or presentation layers. Clients, repositories, executors, and factories may support those responsibilities without becoming new layers.

| Layer | Owns | Must not own in migrated paths |
| --- | --- | --- |
| Views | Widgets, focus, visual selection, display, input, concrete dialogs | SDK clients, persistence, relationship/collection rules |
| Controllers | Coordination, confirmation flow, work execution/delivery, reusable formatting | SDK implementation details or direct storage mutation |
| Sessions/model | Account state, public operations, capabilities and domain policies | wx dialogs, speech/braille, sounds, controller knowledge |

Startup connects dependencies. The invisible interface is presentation and must use the same operations as the GUI. Selection belongs to presentation; collection identity, contents and order belong to the model. Existing compose/templates modules contain presentation formatting: separate responsibility before moving files. Do not introduce common provider hierarchies merely because interfaces look alike.

Preserve entry points, configuration, cache formats, IDs, keyboard commands and events through adapters while consumers migrate. Do not combine storage-format changes, concurrency redesign and architectural extraction in one PR.

## Evidence and current progress

The [static inventory](architecture-inventory.md) records definitions, keyboard actions, pubsub producers/consumers, direct API calls, syntax errors and duplicate methods without importing TWBlue. A definition/menu is not proof of reachability or working provider support. Dynamic paths require manual review. Add newly discovered paths before migrating them.

```powershell
./.venv/Scripts/python.exe scripts/generate-architecture-inventory.py
```

The active suite has **177 passing tests**. Collection and persistence fixtures are repaired; obsolete tests for removed APIs were deleted by agreement. Both profile dialogs have controllers, reusable formatting, session-side policies, background operations, lifecycle guards, confirmations, nonmodal success feedback and focus-preserving refresh. The maintainer manually validated Bluesky and Mastodon profiles. GoToSocial inheritance has automated checks; separate real-server GoToSocial validation has not been recorded.

Bluesky authorization verifies credentials before creating/saving account data. Failed legacy-settings conversion restores in-memory settings for a later retry. Other entry points remain legacy; migrated profile dialogs do not complete every relationship or image workflow.

| Completed work | Commit evidence |
| --- | --- |
| Active test discovery and isolated persistence | `71a74526` |
| Bluesky authorization/configuration tests | `bd9d89cf` |
| Save credentials after verified login | `ced27119` |
| Retry failed settings conversion | `d7277f6c` |
| Bluesky profile separation | `f6f08868` |
| Mastodon/GoToSocial operations and relationship policy | `d884ff42` |
| Bluesky focus and feedback | `6b17dbfd` |
| Mastodon profile and consistent interactions | `e091155b` |

## Tracking conventions

Track 115 use cases, 22 architecture tasks and 16 testing tasks. An unchecked box means migration/verification is incomplete, not that the feature is absent. Close an item only when every listed operation meets its acceptance criteria and the definition of done. Reference IDs in PRs and link completed work to evidence. Characterize defects, but fix them explicitly rather than making buggy behavior a permanent requirement.

Initial evidence states: **I** implemented; **P** partial/inconsistent/stub; **D** declared without confirmed working route; **H** historical. These describe the initial audit rather than current runtime guarantees. Providers: **M** Mastodon, **B** Bluesky (`blueski` internally), **G** GoToSocial. M/G requires capability verification, not assumed parity. File/class/line references are in the inventory.

## Compatibility tasks

- [ ] **AR-01** Record signatures, results, exceptions and side effects before extraction. Acceptance: representative characterization tests and explicit pre-existing defects.
- [ ] **AR-02** Preserve public imports/entry points by delegation. Acceptance: old/new consumers share one implementation of rules.
- [ ] **AR-03** Keep one source of state while session.db remains public. Acceptance: old/new access agrees with dict and SqliteDict, without synchronized copies.
- [ ] **AR-04** Preserve account/buffer identities, config namespaces, cache keys and templates. Acceptance: older fixtures retain meaning and extraction does not change formats.
- [ ] **AR-05** Document pubsub payloads, ordering, producers/consumers, threads and lifetime. Acceptance: end-to-end event tests, no duplicate inserts/announcements or callbacks after close.
- [ ] **AR-06** Define per-operation results/errors without a universal redesign. Acceptance: success, cancel, empty, unsupported and failure distinguished; adapters preserve old contracts.
- [ ] **AR-07** Preserve provider capabilities/unavailable actions. Acceptance: no unsupported menu/shortcut calls; G retains its overrides.
- [ ] **AR-08** Inject collaborators with compatible defaults. Acceptance: migrated operations testable with fake clients/storage and no real UI/network.

## Use-case catalog

### A. Startup, accounts and lifetime (E3; all providers)

Sources: main.py, sessionmanager, base/provider sessions and mainController.

- [ ] **CU-A01** Portable/installed startup, paths, logs, languages and native dependencies. Acceptance: injectable paths, both modes verified, no import-time writes in new modules.
- [ ] **CU-A02** Existing-instance/stale-PID checks. Acceptance: live, invalid and missing process decisions independent of dialogs.
- [ ] **CU-A03** Discover saved/current/ignored accounts. Acceptance: equivalent M/B/G classification, including legacy atprotosocial config, without windows.
- [ ] **CU-A04** Malformed/incomplete account folders/settings. Acceptance: temporary fixtures specify skip/keep/delete; cancellation/errors cannot delete valid accounts. Change automatic cleanup as an explicit fix.
- [ ] **CU-A05** M/G authorization: instance, app registration, browser URL/code. Acceptance: success/cancel at each step, unreachable instance, invalid code and no valid account from partial authorization.
- [ ] **CU-A06** B handle/App Password authorization. Acceptance: success/cancel/rejection, model operation without wx and credentials saved only after verification. Saving defect fixed; authorization extraction pending.
- [ ] **CU-A07** Saved login, credential verification, identity/preferences. Acceptance: equivalent restored state, distinct expiry/network errors and no duplicate buffers.
- [ ] **CU-A08** Initial/current account, ignored startup accounts and manual retry. Acceptance: focus/retry cannot change destination account accidentally.
- [ ] **CU-A09** Logout/remove accounts. Acceptance: stop workers, remove buffers, update registry/config, release resources, preserve data on cancel.
- [ ] **CU-A10** Exit/confirm/save/restart. Acceptance: ordered single shutdown despite save errors; no timers/subscriptions/pollers/clients remaining for closed accounts.

### B. Profiles, identity and relationships (E2)

Sources: provider profile dialogs, handlers/userActions/userList, user buffers, userAlias and sessions.

- [x] **CU-B01** B profile lookup from post/list/identifier. Acceptance: controller uses get_profile, view receives prepared values; identity/bio/counts/relationship, empty/error/late responses verified. Profile commits and maintainer validation recorded above.
- [ ] **CU-B02** M/G profile lookup preserving HTML/fields/dates/images. M implemented and manually validated in e091155b; separate G real-server verification remains pending.
- [ ] **CU-B03** Resolve IDs/handles/remote accounts/notification authors and own identity. Acceptance: no private clients in migrated views; nonexistent/self cases across entry points.
- [ ] **CU-B04** Download/decode/scale avatars/banners. Acceptance: formats/transparency, missing/invalid images, late results. Profiles migrated; other consumers such as editing remain open.
- [ ] **CU-B05** Follow/unfollow. Acceptance: correct IDs/B relationship URIs, state updated only on success, no repeated mutations. Profiles done; other entry points pending.
- [ ] **CU-B06** Mute/unmute. Acceptance: provider-specific effects/errors consistent across entry points with B05 guarantees.
- [ ] **CU-B07** Block/unblock. Acceptance: correct relation IDs, consistent state/collections and cancellation/errors across entry points.
- [ ] **CU-B08** Own/other followers/following: open/page/restore. Acceptance: model-owned cursors/hydration, no duplicates or mixed-account data.
- [ ] **CU-B09** Blocked/muted lists where supported. Acceptance: explicit capabilities, no operations forbidden by G overrides.
- [ ] **CU-B10** Post likers/favoriters/sharers. Acceptance: pagination, hydrated fields, empty results and profile navigation preserved.
- [ ] **CU-B11** Edit profile (M/G implemented, B hidden). Acceptance: save/cancel/failure preserves fields/resources; no accidental B enablement.
- [ ] **CU-B12** Add/edit/delete/manage local aliases (M; B declaration). Acceptance: persistence/rendering equivalent without enabling unsupported B features.

### C. Composition and publication (E4)

Sources: basic/provider message controllers/dialogs, base buffers, sessions and translation/spelling/completion extras. Reconcile the generic composer under L03.

- [ ] **CU-C01** Compose/publish text, account choice and limits. Acceptance: pure validation, equivalent payload, no duplicate sends or publication after cancel.
- [ ] **CU-C02** Reply recipients/context. Acceptance: correct ID/URI/root/parent and existing own-mention exclusion rules.
- [ ] **CU-C03** Quote posts including M fallback. Acceptance: equivalent payload/fallback URL and rendering; distinguish repost from quote.
- [ ] **CU-C04** Language, sensitivity/CW and supported visibility. Acceptance: capabilities outside widgets, values retained on draft recovery.
- [ ] **CU-C05** M/G multi-post drafts, add/remove and per-post data. Acceptance: reply chain/order, specified partial failure and no silent republication on retry.
- [ ] **CU-C06** Add/remove images and alt text. Acceptance: order/limits/metadata/uploads and retained draft/files on errors.
- [ ] **CU-C07** Audio/video attachments and metadata. Acceptance: provider type/limit matrix, explicit unsupported rejection, processing outside dialogs.
- [ ] **CU-C08** M/G polls: choices/duration/multiple selection. Acceptance: validation/payload without wx; cancel/edit behavior preserved.
- [ ] **CU-C09** B facets/mentions/links/embeds/IDs/labels. Acceptance: UTF-8 indices, Unicode, quote/link/image/missing context; no network in visual validation.
- [ ] **CU-C10** Recover failed drafts and present results. Acceptance: text/files/context retained, one announcement and compatible exceptions.
- [ ] **CU-C11** M/G edit posts/media. Acceptance: load/change/cancel/error, stable identity and updates in all collections.
- [ ] **CU-C12** LibreTranslate/DeepL. Acceptance: language/engine/timeouts/errors with fake transport; no blocked UI or config writes on cancel.
- [ ] **CU-C13** Spelling suggestions/ignore/replace/replace-all/dictionary additions. Acceptance: missing dictionary/cancel, state independent of dialogs.
- [ ] **CU-C14** Completion/manual user entries. Acceptance: repository queries separate from menus, correct insertion, commented/missing completion references reviewed.
- [ ] **CU-C15** M follower/following completion scan/progress/origin. Acceptance: paginated worker without widgets, controller-delivered progress, existing entries preserved on error.

### D. Post actions and reading (E4/E6)

Sources: main controller, provider base buffers/handlers/messages/sessions, compose/templates/utils.

- [ ] **CU-D01** Full post, metadata, sensitive content and descriptions. Acceptance: dict/SDK fixtures and no network from view.
- [ ] **CU-D02** Boost/repost/remove and share-or-quote choice. Acceptance: configured mode, correct URI/CID/ID, no private/unsupported sharing.
- [ ] **CU-D03** Add/remove/toggle like/favorite. Acceptance: one mutation, consistent state/counts, same operation from menu/shortcut.
- [ ] **CU-D04** M/G bookmarks. Acceptance: post/collection agree and failure never announces success.
- [ ] **CU-D05** Delete own posts. Acceptance: permissions/confirm/cancel/remote delete and model removal from all collections.
- [ ] **CU-D06** M/G pin/unpin. Acceptance: permissions, updates and pinned ordering in both directions.
- [ ] **CU-D07** M/G votes/results. Acceptance: single/multiple, expired/already voted and update without UI mutation.
- [ ] **CU-D08** M/G conversation mute/unmute/cleanup. Acceptance: thread/mentions/collections consistent and cleanup events characterized.
- [ ] **CU-D09** Browser post URLs/content links/tags. Acceptance: pure extraction, zero/one/multiple links, correct destination, browser only in presentation coordination.
- [ ] **CU-D10** Clipboard/repeat item. Acceptance: equivalent complete content without model mutation/network.
- [ ] **CU-D11** OCR. Acceptance: image/language/empty/error/progress; reconcile disabled menu versus buffer paths.

### E. Collections, timelines, search and filters (E5)

Sources: provider buffers/handlers, session ordering/update/routing and other_buffers settings.

- [ ] **CU-E01** Default account buffers/capabilities/titles. Acceptance: stable hierarchy/names; deciding existence does not construct widgets.
- [ ] **CU-E02** M/G home/local/sent/favorite/bookmark loads. Acceptance: parameters in session, equivalent content/order, old data retained on failure.
- [ ] **CU-E03** B Following/Discover/feed resolution. Acceptance: correct feed/fallback and separate cursors.
- [ ] **CU-E04** Mentions/notification context. Acceptance: provider selection/hydration/dedup outside controller; distinguish posts/events.
- [ ] **CU-E05** Notifications/associated-post actions/dismissal. Acceptance: missing posts, correct dismissal type, consistent counters.
- [ ] **CU-E06** M/G announcements/read/dismiss. Acceptance: consistent state/removal, unsupported post actions disabled.
- [ ] **CU-E07** Open/restore user timelines. Acceptance: stable identity/pinned/filter behavior, no duplicate buffers.
- [ ] **CU-E08** Remote-instance local/federated timelines. Acceptance: model-owned community client, correct URL/account/paging.
- [ ] **CU-E09** Remote searches/restore. Acceptance: preserved term/type/mode/cursor per provider; close removes only matching config.
- [ ] **CU-E10** Local content search. Acceptance: no network, position/direction and no-match behavior.
- [ ] **CU-E11** Manual refresh/missing recovery/older items. Acceptance: reconcile duplicate get_more_items, real methods per buffer, no nonexistent panels.
- [ ] **CU-E12** Periodic/forced refresh/interval. Acceptance: fake clock/executor, no overlapping calls or UI block.
- [ ] **CU-E13** Batch merge/dedup/order/pinned/limits. Acceptance: provider fixtures, repeated batches/missing IDs/dict/SDK, disk-memory equivalence.
- [ ] **CU-E14** Update existing post in all buffers. Acceptance: stable identity/selection, no update-event insertion duplicates.
- [ ] **CU-E15** Clear/close/destroy buffers and confirmations. Acceptance: model owns data/config changes before view removal; clear differs from collection deletion.
- [ ] **CU-E16** Persist/restore order/open buffers/reading position. Acceptance: reconstruction by identity despite changed counts/ignored accounts.
- [ ] **CU-E17** M server filters/words/contexts CRUD. Acceptance: API outside form controllers, existing filters retained on cancel/error.
- [ ] **CU-E18** M filter rendering. Acceptance: correct context/hide/warn and data/selection/row alignment.
- [ ] **CU-E19** Declared/historical lists/membership/trends/settings. Acceptance: classify each consumer as supported/disabled/historical, no new feature implementation disguised as extraction.

### F. Conversations and private messages (E5 after E4)

Sources: M conversations, B chat/timeline buffers, handlers, B conversation operations, M private composition.

- [ ] **CU-F01** M/G conversation list/private context. Acceptance: participants/last message/order retained, invalid public actions unavailable.
- [ ] **CU-F02** M/G private send/reply. Acceptance: correct recipients/privacy/reply; never fall back to public posting.
- [ ] **CU-F03** B chat-list merge. Acceptance: model owns conversation/member/last-message identity fallbacks; no refresh duplicates.
- [ ] **CU-F04** B create/get/open chat. Acceptance: correct account/members, recipient restrictions, empty conversations.
- [ ] **CU-F05** B messages/order/older pages. Acceptance: characterize actual ChatBuffer.get_more_items before claiming paging; cursors/merge in model.
- [ ] **CU-F06** B chat send/reply. Acceptance: conversation ID/text, retained state on failure and single announcement/insertion.
- [ ] **CU-F07** Members/last message/individual-message rendering. Acceptance: equivalent accessible text/author/date, incomplete records and alternate field forms.

### G. Streaming, polling and events (E7)

Sources: provider session/streaming, main-controller subscribers, thread utilities and repeating timer.

- [ ] **CU-G01** M/G start/stop/check streams and settings. Acceptance: repeated start/stop safe, no closed-account delivery, global/account disable respected.
- [ ] **CU-G02** M/G posts/edits/notifications/conversations and routing. Acceptance: account checked before mutation, one model update, UI projection on UI thread.
- [ ] **CU-G03** B polling/initial watermark. Acceptance: fake clock/transport, silent initial baseline, ordered/missing-watermark/repeated batches.
- [ ] **CU-G04** B mention/reply/follow topics. Acceptance: identify missing consumers, explicitly retain compatibility or connect; do not invent consumers to justify dead code.
- [ ] **CU-G05** Sound/autoread/count feedback. Acceptance: same mute/autoread policy for streaming/manual/periodic refresh, no duplicate announcements.
- [ ] **CU-G06** Worker failure/reconnect/retry/shutdown. Acceptance: explicit per-operation policies, no automatic non-idempotent publication retries or callbacks into closed views.

### H. Presentation, navigation and accessibility (E6)

Sources: frame/tray, main controller, base buffers, keyboard handler/editor, output/sound, compose/templates/utils and tutorial.

- [ ] **CU-H01** Previous/next item, home/end/pages. Acceptance: empty/boundary/reverse cases and equivalent position announcements.
- [ ] **CU-H02** Buffer/account switch and placeholder resolution. Acceptance: selection and operation account agree for empty/ignored accounts.
- [ ] **CU-H03** Show/hide/tray/initial invisible mode. Acceptance: focus/shortcut registration preserved, same functional operations in both interfaces.
- [ ] **CU-H04** Register/unregister shortcuts and dynamic actions. Acceptance: every action/keymap has a supported destination; review interact and other apparent missing handlers.
- [ ] **CU-H05** Edit/restore/switch keymaps/restart. Acceptance: conflict/cancel/save and historical command names preserved.
- [ ] **CU-H06** Provider/buffer menu capabilities. Acceptance: hide/restore preserves bindings and never operates on previous account.
- [ ] **CU-H07** Row/speech formatting for all item types. Acceptance: formatting outside session operations, equivalent provider/dict/SDK fixtures.
- [ ] **CU-H08** Dates/language/offsets/aliases/emoji/safe text/HTML/sensitivity. Acceptance: explicit clock/language tests, no reliance on another test installing translation globals.
- [ ] **CU-H09** Edit/validate/restore templates. Acceptance: current variables/persisted templates compatible, import wrappers retained for old consumers.
- [ ] **CU-H10** Focused/long-item reading and position/status. Acceptance: fake speech/braille sink, interruption policy and manual screen-reader check.
- [ ] **CU-H11** Buffer/account mute and autoread toggles. Acceptance: persisted settings, consistent notifications without per-buffer policy copies.
- [ ] **CU-H12** Media indicators and ready/error sounds. Acceptance: no sound dependencies in migrated sessions, equivalent presentation policy.
- [ ] **CU-H13** Playback/URL/volume/seek. Acceptance: preserved increments/limits, resolver separate from player/widgets.
- [ ] **CU-H14** Devices/sound packs/tutorial. Acceptance: preview/cancel/save, missing resources, account isolation.

### I. Configuration, persistence and conversions (E1/E3/E8)

Sources: config/config_utils/paths/defaults, base session, B legacy conversion, settings controllers and completion storage.

- [ ] **CU-I01** Load/validate/default/save global/account settings. Acceptance: valid/missing/invalid/write failures, no loading-side dialogs.
- [ ] **CU-I02** B atprotosocial conversion and old templates. Acceptance: idempotence/custom values/old-new fixtures/write failure preserves original. Retry defect fixed; full separation pending.
- [ ] **CU-I03** Global language/window/voice/exit/update/streaming/keymap preferences. Acceptance: explicit immediate/restart policy, no write on cancel.
- [ ] **CU-I04** Proxy/translation settings. Acceptance: construction outside forms, preserved restart policy and no secrets in logs/results.
- [ ] **CU-I05** Account buffer activation/order, reading/names/emoji/limits/storage/audio. Acceptance: view collects, model validates/applies; B uses real handler path rather than invalid forms.
- [ ] **CU-I06** Memory/disk cache save/restore. Acceptance: size 0/-1/positive, both orders, cursors/heterogeneous values, equivalent backends.
- [ ] **CU-I07** Corrupt cache/I/O recovery. Acceptance: current policy characterized, resources closed, observable errors without storage-side speech; delete/rebuild changes explicit.
- [ ] **CU-I08** Commit/close databases and save at exit. Acceptance: no residual locks/GC dependency; nested SqliteDict changes survive reopen.
- [ ] **CU-I09** SQLite completion by user/origin. Acceptance: temporary fixtures, duplicate/search/origin deletion without account mixing.

### J. Support, updates and diagnostics (E8)

Sources: main controller, diagnostics/memory, updater/restart/logger/application/setup/build scripts.

- [ ] **CU-J01** Help/changelog/about/site/sound-pack/bug-report. Acceptance: coordination chooses routes/data, adapters present, tests never open browser.
- [ ] **CU-J02** First-run donation and display state. Acceptance: first/subsequent/cancel/link preserved.
- [ ] **CU-J03** Manual/automatic updates, consent/download/progress/extract/bootstrap. Acceptance: fake transport/process, each stage failure, supported cancel; never install updates in tests.
- [ ] **CU-J04** Source memory/CPU/thread diagnostics. Acceptance: independent snapshot, stopped timer, source-only visibility.
- [ ] **CU-J05** Logging/stdout/stderr for source/frozen. Acceptance: explicit setup/path failure handling, model imports do not redirect streams.
- [ ] **CU-J06** Portable/installer packaging. Acceptance: build/startup/shutdown smoke tests for moved modules/defaults/translations/audio/paths.

### L. Partial and historical routes (E0)

- [ ] **CU-L01** Removed Twitter tests and remaining defaults/comments/keymaps. Tests deleted by agreement. Acceptance: document names still serving contracts and transplant applicable intentions without obsolete SDKs.
- [ ] **CU-L02** Invalid B settings/user-list modules. Acceptance: inspect imports/consumers, explicitly repair current API or retire unreachable code; distinguish working settings routes.
- [ ] **CU-L03** Generic composeDialog and handle_compose_dialog_send versus active Post. Acceptance: verify approve/compose_panel/async paths, one canonical coordinator plus required adapters; do not activate broken paths.
- [ ] **CU-L04** B action/message/user-command stubs. Acceptance: document real consumers; returning None is not a completed feature.
- [ ] **CU-L05** Duplicate Controller.get_handler/get_more_items. Acceptance: characterize effective final definitions, compare discarded branches and preserve public entries.
- [ ] **CU-L06** asyncio.create_task, NotificationError, logger/log, session.KIND and missing panels. Acceptance: executable contracts/tests for reachable paths; fix defects before extraction.

## Testing backlog

- [x] **T-01 (E1)** Repair complete discovery and classify removed APIs explicitly instead of generic skips. Acceptance: clean active collection and documented removal/replacement; 71a74526.
- [x] **T-02 (E1)** Temporary persistence paths, valid config, explicit closure/reversible patches. Acceptance: no cwd changes, real config/testing writes or sys.modules pollution; 71a74526.
- [ ] **T-03 (E1)** Extend disk/memory by zero/unlimited/limited size by order with reopen checks; corruption/write/cursor/nested data. Acceptance: persisted contents, not just types.
- [x] **T-04 (E1/E3)** Current synchronous B client/settings tests. Acceptance: login/resume/rejection/cancel/legacy namespace without approve; bd9d89cf, ced27119, d7277f6c.
- [ ] **T-05 (E1/E6)** Transfer useful Twitter test intentions to M/B. Acceptance: current fixtures/variables, fixed clocks, no tweepy dependency.
- [x] **T-06 (E2)** Profile controller tests with fake view/executor/session and wx integration. Acceptance: success/empty/error/late results and observable effects; f6f08868, 6b17dbfd, e091155b.
- [ ] **T-07 (E3)** Account/config discovery/auth/login/retry/ignore/remove/conversion/start-stop/G contracts. Acceptance: A/I scenarios with old temporary fixtures, no real accounts.
- [ ] **T-08 (E4)** Text/reply/quote/thread/media/alt/poll/facets/like/repost/edit/delete and partial failure. Acceptance: provider payload/state verified, no actual publication.
- [ ] **T-09 (E5)** Paging/cursors/pinned/dedup/filters/chat merge/hydration, dict/SqliteDict, selection identity. Acceptance: multiple pages/repeated batches per provider.
- [ ] **T-10 (E6)** Readable rendering fixtures, fake speech/braille/sound. Acceptance: visible/invisible equivalence and one announcement per intention.
- [ ] **T-11 (E7)** Account routing/UI thread/start-stop/unsubscribe/late callbacks/timers. Acceptance: fake clock/executor, no network sleeps or order dependency.
- [ ] **T-12 (E8)** OCR/translation/audio/update fake adapters. Acceptance: failure/cancel without browser, installing updates or real services.
- [ ] **T-13 (from E1)** Windows PR CI for collection/active suite. Acceptance: reproducible Python 3.13/dependencies; define supported matrix before adding 3.10. Release currently does not run pytest.
- [ ] **T-14 (each stage)** Static boundaries with temporary legacy exceptions. Acceptance: no new UI imports in migrated model or SDK calls in views; exceptions have IDs/removal plans.
- [ ] **T-15 (each stage)** Record visible/invisible screen-reader/provider smoke checks. Acceptance: input/focus/feedback/cancel/error/close documented; credentials excluded. Profiles validated, other paths pending.
- [ ] **T-16 (E1/E8)** Independent processes/different test orders. Acceptance: no global translation/sound/mock/resource leakage between files.

## Remaining architecture tasks

- [ ] **AR-09 (E0)** Classify P/D/H routes by call sites/imports/menus/shortcuts. Acceptance: L01-L06 decisions distinguish canonical paths/adapters/unreachable code.
- [x] **AR-10 (E2)** First injectable profile controller. Acceptance: B01/T06 validated before repeating pattern; f6f08868 and maintainer validation.
- [ ] **AR-11 (E3)** Account catalog/lifetime/provider factory. Acceptance: sessions.sessions/manager.manager remain adapters without duplicate registries, A03-A10 verified.
- [ ] **AR-12 (E3)** Authorization SDK/presentation separation. Acceptance: session receives inputs, controller coordinates dialogs/browser, old methods delegate.
- [ ] **AR-13 (E4)** Canonical send path and account operations; independent draft validation when useful. Acceptance: C01-C11/L03 no longer mix foreign APIs.
- [ ] **AR-14 (E5)** Encapsulate collection reads/mutations before replacing db. Acceptance: no direct assignment/pop in migrated consumers; persistent values reassigned/committed.
- [ ] **AR-15 (E5)** Move timeline queries/paging/hydration/merge from buffers. Acceptance: no SDK parameters/community clients in controllers.
- [ ] **AR-16 (E6)** Formatting/accessible-feedback boundaries within three layers. Acceptance: sessions do not speak/play sounds, wrappers preserve old compose/templates imports and outputs.
- [ ] **AR-17 (E7)** Worker/UI dispatcher with lifetime/cancellation. Acceptance: retain current threads initially, explicit event-loop owner, observable errors, live-target checks.
- [ ] **AR-18 (E7)** Pubsub subscription/lifetime. Acceptance: old topics compatible, no widgets in model events, logout/close unsubscribes.
- [ ] **AR-19 (E8)** Config/storage versus error presentation. Acceptance: config_utils/persistence no wxUI/output imports, explicit recovery policy.
- [ ] **AR-20 (E8)** Split mainController by proven coordination boundaries. Acceptance: facade/commands/shortcuts preserved; more than moving methods into another large class.
- [ ] **AR-21 (E8)** Remove outside-model API/private-client/mutable-db access in migrated routes. Acceptance: no crossings or explicit compatibility exceptions; retain APIs with consumers.
- [ ] **AR-22 (E8)** Docs/build and future adapter-retirement policy. Acceptance: version/consumers/conversion documented; removing compatibility is a later explicit decision.

## Delivery sequence

Stages are dependencies, not large PRs. Characterize high-risk persistence/streaming early even if extracting them later. Repair defects separately before extracting those paths.

| Stage | Deliverable | Dependency and completion |
| --- | --- | --- |
| E0 | Effective routes and historical/broken-code decisions | L01-L06/AR09 for affected paths |
| E1 | Reliable tests/fixtures/first CI | E0 test decisions, T01-T05/T13/T16; not complete |
| E2 | Profile/relationship vertical slices | Sufficient E1 coverage; B01 then B02-B12; dialogs done, G server/other routes pending |
| E3 | Accounts/auth/basic config/shutdown | E1/E2, A01-A10/I01/I02/T07 |
| E4 | Composition/publication/post actions | E3/L03/L06, C01-C15/D02-D08/T08; one operation/provider per PR |
| E5 | Collections/search/conversations/paging | E3/E4/db contract, E01-E19/F01-F07/T09 |
| E6 | Presentation/accessibility/media | Can advance per use case, D01/D09-D11/H01-H14/T10 |
| E7 | Streams/events/timers/UI delivery | Collection/feedback contracts, G01-G06/T11 |
| E8 | Full persistence/support/facade/distribution | E3-E7, I03-I09/J01-J06/T12/T14/T15/AR19-AR22 |

## Definition of done

- Record IDs/provider/visible-invisible entry points and bounded PR scope.
- Characterize old behavior or explicitly document/fix/test a defect.
- Test model operations with fake dependencies without real UI/network.
- Keep SDK/storage out of views and direct storage mutation out of migrated controllers.
- Preserve imports/signatures/results/exceptions/events/data, or provide explicit compatible adapters.
- Cover success/cancel/empty/unsupported/failure as appropriate; no duplicate sends/inserts/announcements.
- Preserve focus/selection, close resources, ignore late results targeting destroyed windows.
- Record actual automated/manual results and distinguish pending verification.
- Regenerate inventory when definitions/events change and link checked tasks to evidence.

## Initial test audit and reproducibility

The initial audit used local Python 3.13.2 and installed wx/image dependencies; no dependencies were installed. Release CI uses 3.13; older README/CLAUDE sections mention 3.10.

| Initial group | Baseline observation | Disposition |
| --- | --- | --- |
| Memory utilities | 4 passed | Retained; process errors/diagnostics lifetime pending |
| Image utilities | 17 passed | Retained format/alpha/path/invalid/scaling/wx regressions |
| B quote formatting | 11 passed | Retained; Unicode/incomplete/SDK/language isolation extensions pending |
| Base session | 8 fixture errors: missing conf.defaults and KeyError general | Fixed valid defaults, temporary paths and explicit resource closure |
| B session | Collection error: missing exceptions and foreign approve/async assumptions | Rewritten for synchronous session; obsolete file removed |
| Twitter | Collection error: tweepy missing and sessions.twitter removed | Deleted by agreement; applicable intentions tracked in T05 |

Initial complete collection found 40 cases and two collection errors, not 40 passes. The selected baseline reached 32 passes using exclusive temporary storage. Intermediate suite results were 44/54/55/63/81/103/129/135/170, then **177 passed**. Credential-before-login and failed-conversion retry defects were corrected rather than preserved as intended behavior.

Existing shared pytest temp/cache directories have access-denied errors. Tests use a fresh exclusive basetemp and disable cacheprovider. No prior directories or ACLs were modified. From repository root:

```powershell
$auditTemp = Join-Path $env:TEMP ('twblue-audit-' + [guid]::NewGuid().ToString('N'))
./scripts/run-tests.ps1 -PytestArgs @('-q','-p','no:cacheprovider','--basetemp',$auditTemp)
```

Pytest owns and may remove its basetemp: never use a directory containing user data. The original base fixture used cwd-relative config/testing and an unreverted sound-module patch; current fixtures avoid both. The original failure was investigated in an isolated temporary cwd with copied defaults and blocked error dialogs before repair.

Automated tests and maintainer profile checks do not certify all accumulated features, real-server G behavior, full accessibility, packaging, or coverage percentages. E1/E2 are not complete. No full rewrite, release, deployment or data-format change is implied by this roadmap. Changelog/release documents are maintained separately.
