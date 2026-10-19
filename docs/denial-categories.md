# Denial categories

This note defines the categories the denial classifier chooses from. It was written before the classifier exists, so nothing here describes working code yet.

## The categories

The classifier returns exactly one of these seven values for each denial note.

1. **`billing_or_coding_error`**
   - Meaning: the claim has missing or wrong data, or a code or modifier problem.
   - Example wording: "Claim is missing the rendering provider NPI."
   - Typical next step: correct the claim and resubmit.
   - Related reason codes (CARC): 16 (missing information or a billing error), 4 (code and modifier do not match), 11 (diagnosis does not fit the procedure), and 97 (service bundled into another) when the bundling can be fixed.

2. **`authorization_issue`**
   - Meaning: required prior approval is absent or was exceeded.
   - Example wording: "No prior authorization on file for this procedure."
   - Typical next step: check whether an authorization exists or can be obtained after the fact, then appeal or resubmit with the authorization number.
   - Related CARCs: 197 (absent), 198 (exceeded).

3. **`medical_necessity`**
   - Meaning: the payer says the service was not medically necessary.
   - Example wording: "Service does not meet medical necessity criteria."
   - Typical next step: review the payer's criteria, request the clinical records, and appeal.
   - Related CARC: 50.

4. **`eligibility_or_coverage`**
   - Meaning: the patient was not covered on the date of service, could not be identified as insured, or the payer is not the responsible one.
   - Example wording: "Coverage terminated before date of service."
   - Typical next step: verify eligibility, then bill the correct payer or the patient.
   - Related CARCs: 27, 31, 109.

5. **`timely_filing`**
   - Meaning: the filing deadline passed.
   - Example wording: "Claim received after the filing limit."
   - Typical next step: appeal with proof of timely original submission, or write the balance off.
   - Related CARC: 29.

6. **`duplicate_claim`**
   - Meaning: the payer believes it already received this claim.
   - Example wording: "Duplicate of a previously submitted claim."
   - Typical next step: check the status of the original claim. If it was paid, no action is needed. If this was not a true duplicate, appeal with proof of the original submission.
   - Related CARC: 18. The X12 list says to use it with group code OA, except where state workers' compensation rules require CO.

7. **`other_or_unclear`**
   - Meaning: the note does not clearly fit any category above.
   - Typical next step: manual review. This is better than a forced guess.

## Rules

- One primary category per note. Real denials can carry several reasons, so this is a simplification and a known limitation.
- The set is closed. The classifier must return one of the seven values above, spelled exactly.
- A category is chosen by the cause stated in the note. Whether a denial is final (hard or soft) is not part of the label.

## Why the list looks like this

- Each category leads to a different next step, because the tool drafts that next step later.
- Some causes were merged on purpose. Coding errors and missing information share a next step (correct and resubmit), and absent or exceeded authorizations share one too.
- Left out on purpose: a separate "documentation requested" category, and splitting eligibility or billing errors into smaller pieces. The test set will be small (roughly 10 to 15 notes), so more categories would leave only one or two notes each.
- With about two notes per category, each note moves the accuracy score by several percentage points. The evaluation is a sanity check, not a statistical claim.

## Sources and limits

- Reason code descriptions were checked against the X12 claim adjustment reason code list (https://x12.org/codes/claim-adjustment-reason-codes) in October 2026. They are paraphrased here, and the X12 list is the authoritative source.
- CARC 15 (authorization number invalid) is deactivated on the X12 list, so it is not used here, even though some vendor sites still mention it.
- The codes are examples, not a complete mapping. Real payers add remark codes (RARCs) and their own wording.
- All notes and payer policies used in this project are invented.
