# Fresh notes run (October 29, 2026)

This is the single scored run of the 8 fresh notes in [`data/fresh_notes.json`](../data/fresh_notes.json), made after the classifier prompt, retrieval, and the drafting prompt were frozen (drafting prompt as of commit `919a4a3`). Each model's output below is copied exactly as `eval_draft.py` printed it. The notes themselves are in the data file.

Command used for each model:

```
.venv\Scripts\python.exe eval_draft.py data/fresh_notes.json --model MODEL_ID
```

(The run read the same file from outside the repo, before it was committed here unchanged.)

## What to look at when reviewing

- Every note's right answer was "no policy applies", so the citation scores only test rejecting candidates. See the README for that limit.
- fresh-06, Haiku: the last sentence of the next step is muddled.
- fresh-06, Sonnet: flagged for mentioning an appeal without a deadline lookup. The step says "Do not resubmit or appeal", so the flag is a false positive.
- fresh-08: Sonnet and Opus say to watch the 45-day appeal window while waiting for the written determination. Haiku does not.

## claude-haiku-5-5

```text
OK   fresh-01 (Copperleaf Health Plan): expected policy None, cited None; candidates ['pol-02']
     category timely_filing (label timely_filing); tool called, deadline 60 days (matches file)
     next step: Before writing this off, search for proof of an earlier accepted submission for CL-73184, such as clearinghouse acceptance reports (999/277CA), payer portal submission logs, or prior correspondence showing the claim was received within the filing limit. If you find proof, submit a written appeal with that documentation through the Copperleaf provider portal within 60 days of the denial date. If no proof is found, do not appeal on timeliness grounds and route the account for write-off review under your timely filing policy.

OK   fresh-02 (Bramblecrest Insurance): expected policy None, cited None; candidates ['pol-05', 'pol-06']
     category billing_or_coding_error (label billing_or_coding_error); no tool call
     next step: Add the required modifier to the claim line that the payer flagged, confirming the correct modifier for this service and date of service before editing. Verify that the corrected line matches the submitted service details, then resubmit the corrected claim as the Bramblecrest representative advised. Keep the authorization reference on the claim, since the representative confirmed approval is already on file.

OK   fresh-03 (Quillfield Health): expected policy None, cited None; candidates ['pol-09', 'pol-07']
     category medical_necessity (label medical_necessity); tool called, deadline 45 days (matches file)
     next step: Pull the clinical records for claim Q-40826 and have the treating provider document why the requested level of treatment was medically necessary, citing the specific clinical findings and criteria the payer applied. Submit that documentation as a reconsideration request through the Quillfield provider portal within 45 days of the denial date. Do not resubmit under the authorization number, because the payer states the denial is based on clinical necessity rather than missing prior approval.

OK   fresh-04 (Copperleaf Health Plan): expected policy None, cited None; candidates ['pol-01', 'pol-02']
     category timely_filing (label timely_filing); tool called, deadline 60 days (matches file)
     next step: Do not resend the claim, since the rep confirmed another copy will not resolve a timely filing denial, and do not treat the duplicate flag as the cause because the earlier submission was for a different service date. Gather proof of timely original submission, such as clearinghouse acceptance reports, payer acknowledgment or rejection files, or portal submission confirmations, and check whether any filing exception request was ever made. Then file a timely filing appeal through the provider portal within 60 days of the denial date, including that proof and the reason the claim was delayed.

OK   fresh-05 (Bramblecrest Insurance): expected policy None, cited None; candidates ['pol-04', 'pol-05']
     category eligibility_or_coverage (label eligibility_or_coverage); no tool call
     next step: Verify the coverage termination date on the payer's eligibility portal and ask the subscriber or employer whether any extension, COBRA continuation, or retroactive enrollment exists that covers the date of service. If active coverage is confirmed for that date, submit a corrected claim with the updated coverage information. If no coverage existed on the date of service, stop billing Bramblecrest, check whether another payer is responsible, and move the balance to patient responsibility only if the patient's contract allows it.

OK   fresh-06 (Quillfield Health): expected policy None, cited None; candidates ['pol-08', 'pol-07']
     category duplicate_claim (label duplicate_claim); no tool call
     next step: Do not resubmit Q-57192 as a new claim, because Q-57191 for the same service date and billed service was already paid and this line would be a second payment for the same service. Compare Q-57191 and Q-57192 line by line to confirm they are exact duplicates. If the earlier submission contained an error, such as a wrong code or modifier, correct it through Quillfield's corrected-claim process and document the reason in the account notes. If no error is found, close Q-57192 as a duplicate and adjust the account so the medical-necessity documentation does not trigger a rebill.

OK   fresh-07 (Copperleaf Health Plan): expected policy None, cited None; candidates ['pol-01', 'pol-02']
     category eligibility_or_coverage (label eligibility_or_coverage); no tool call
     next step: Verify the coordination-of-benefits order and the primary payer on the coverage record for the date of service, and confirm with the patient or the other payer whether that payer is primary. If another payer is primary, route the claim to that payer first and do not resubmit it to Copperleaf until the primary payer's determination is on file. Then send Copperleaf the primary payer's determination and the COB information so it can reassess payment responsibility, and note that no CARC was provided so the remittance detail should be requested to confirm the denial reason.

OK   fresh-08 (Quillfield Health): expected policy None, cited None; candidates ['pol-07', 'pol-08']
     category other_or_unclear (label other_or_unclear); no tool call
     next step: Request a written determination from Quillfield Health that states the specific denial reason and the requirement not met, and ask for the CARC and remark codes in writing. Also pull the claim's electronic remittance advice or the paper EOB and check the line-level adjustment codes, since the summary remittance may omit them. Hold the claim in denied status with a note of the provider services call, including the date, rep name, and the confirmed facts (timely filing, coverage period, and authorization all verified), until the written determination arrives and identifies the cause.

8 of 8 citations correct (claude-haiku-5-5, C:\Users\thein\Documents\fresh-notes.json)
  cited the right snippet: 0 of 0
  correctly cited none: 8 of 8
  citations outside the candidates: 0
  tool called on 3 notes; deadline matched the file on 3
  steps that mention an appeal without a deadline lookup (check by hand): 0
  classifier category correct: 8 of 8
tokens in: 26799, out: 5004, estimated cost: $0.0052, time: 45s
```

## claude-sonnet-5-5

```text
OK   fresh-01 (Copperleaf Health Plan): expected policy None, cited None; candidates ['pol-02']
     category timely_filing (label timely_filing); tool called, deadline 60 days (matches file)
     next step: Do one more search for proof of timely filing on CL-73184, such as clearinghouse acceptance reports, payer acknowledgments, or earlier submission records. If you find proof of an earlier accepted submission, file an appeal through the provider portal within 60 days of the denial date, and attach that proof. If you find nothing, send the claim for write-off review under your internal policy, because the denial is valid and the patient cannot be billed on this basis unless your contract allows it.

OK   fresh-02 (Bramblecrest Insurance): expected policy None, cited None; candidates ['pol-05', 'pol-06']
     category billing_or_coding_error (label billing_or_coding_error); no tool call
     next step: Review the claim line for BR-62057 against the procedure code and the service documentation, and identify which modifier is required. Add the correct modifier to the line and resubmit the corrected claim, as the payer rep advised. Note the call details in the account, and don't pursue the authorization issue, because the rep confirmed approval is on file.

OK   fresh-03 (Quillfield Health): expected policy None, cited None; candidates ['pol-09', 'pol-07']
     category medical_necessity (label medical_necessity); tool called, deadline 45 days (matches file)
     next step: Pull the clinical records for Claim Q-40826 and confirm they support the level of treatment billed. This includes progress notes, the treatment plan, and documentation of why that level of care was needed. Submit a reconsideration request with this additional clinical documentation through the Quillfield provider portal within 45 days of the denial date, and include the authorization number already referenced.

OK   fresh-04 (Copperleaf Health Plan): expected policy None, cited None; candidates ['pol-01', 'pol-02']
     category timely_filing (label timely_filing); tool called, deadline 60 days (matches file)
     next step: Do not resubmit another copy of the claim, because the rep confirmed that will not resolve the denial and the duplicate flag does not apply (the earlier claim has a different service date and its own adjudication record). Search for proof of timely filing, such as a clearinghouse acceptance report or payer acknowledgment dated within the contracted filing window. If you find it, submit an appeal through the provider portal with that proof within 60 days of the denial date. If you find no proof, write the claim off per your timely filing adjustment policy.

OK   fresh-05 (Bramblecrest Insurance): expected policy None, cited None; candidates ['pol-04', 'pol-05']
     category eligibility_or_coverage (label eligibility_or_coverage); no tool call
     next step: Run an eligibility check for the date of service to confirm the coverage termination date, and ask the patient whether they have other active coverage, such as a new employer plan or a spouse's plan. If other coverage is found, update the registration and bill that payer. If none is found, follow your practice's process to transfer the balance to patient responsibility and write off the claim as appropriate.

OK   fresh-06 (Quillfield Health): expected policy None, cited None; candidates ['pol-08', 'pol-07']
     category duplicate_claim (label duplicate_claim); no tool call, but the step mentions an appeal or reconsideration (check by hand)
     next step: Do not resubmit or appeal Q-57192, because Q-57191 was already adjudicated and paid for the same service date and billed service. Confirm in the remittance that Q-57191 paid correctly, then write off or close Q-57192 as a duplicate. If you find an error on Q-57191, such as a wrong code or modifier, follow Quillfield's corrected-claim process for that original claim instead of sending another claim.

OK   fresh-07 (Copperleaf Health Plan): expected policy None, cited None; candidates ['pol-01', 'pol-02']
     category eligibility_or_coverage (label eligibility_or_coverage); no tool call
     next step: Check the patient's coverage for the date of service and confirm which payer is primary. Do this by contacting the patient or the other payer, or by running an eligibility check. If Copperleaf is secondary, bill the primary payer first. Then send Copperleaf the primary payer's remittance or explanation of benefits with the coordination-of-benefits details. If Copperleaf is in fact primary, collect documentation that shows this, such as a primary-payment determination or a coordination-of-benefits exception, and include it with the resubmission.

OK   fresh-08 (Quillfield Health): expected policy None, cited None; candidates ['pol-07', 'pol-08']
     category other_or_unclear (label other_or_unclear); tool called, deadline 45 days (matches file)
     next step: Submit a written request to Quillfield Health for a written determination that states the specific adjustment reason (CARC/RARC) and the unmet requirement for claim Q-90835, and record the date of the request and the rep's name from the call. Because the cause is still unknown, don't send a corrected claim yet. If the written determination is not received in time, file an appeal through the provider portal within 45 days of the denial date to protect appeal rights.

8 of 8 citations correct (claude-sonnet-5-5, C:\Users\thein\Documents\fresh-notes.json)
  cited the right snippet: 0 of 0
  correctly cited none: 8 of 8
  citations outside the candidates: 0
  tool called on 4 notes; deadline matched the file on 4
  steps that mention an appeal without a deadline lookup (check by hand): 1
  classifier category correct: 8 of 8
tokens in: 28590, out: 4186, estimated cost: $0.0990, time: 55s
```

## claude-opus-5-5

```text
OK   fresh-01 (Copperleaf Health Plan): expected policy None, cited None; candidates ['pol-02']
     category timely_filing (label timely_filing); tool called, deadline 60 days (matches file)
     next step: Search the clearinghouse and practice management records for CL-73184 for any proof of an earlier accepted submission, such as a clearinghouse acceptance report (277CA/999) or an earlier payer rejection showing it arrived before the filing limit. If you find that proof, submit a reconsideration request with the documentation through the Copperleaf provider portal within 60 days of the denial date. If no proof exists, do not resubmit the claim; adjust the balance as a timely-filing write-off under practice policy and do not bill the patient for it.

OK   fresh-02 (Bramblecrest Insurance): expected policy None, cited None; candidates ['pol-05', 'pol-06']
     category billing_or_coding_error (label billing_or_coding_error); no tool call
     next step: Review the denied line on claim BR-62057 against the procedure code and the medical record, and add the missing required modifier (CARC 4). Also make sure the service details on that line support the code as billed. Then send a corrected claim to Bramblecrest Insurance, as the provider services rep advised, and write down the call reference in the account notes.

OK   fresh-03 (Quillfield Health): expected policy None, cited None; candidates ['pol-09', 'pol-07']
     category medical_necessity (label medical_necessity); tool called, deadline 45 days (matches file)
     next step: Get the additional clinical documentation for claim Q-40826 from the rendering provider, such as progress notes, assessment findings, treatment history and the provider's reasoning, showing why this level of treatment was medically necessary. Submit a reconsideration request with that documentation through the Quillfield Health provider portal within 45 days of the denial date. Neither candidate policy was cited: the denial is for medical necessity (CARC 50), not prior authorization or eligibility.

OK   fresh-04 (Copperleaf Health Plan): expected policy None, cited None; candidates ['pol-01', 'pol-02']
     category timely_filing (label timely_filing); tool called, deadline 60 days (matches file)
     next step: Don't resubmit CL-29643. The rep confirmed another copy won't fix the timely filing denial (CARC 29), and the duplicate flag isn't the real cause. Check the practice's records for proof that the claim was filed on time, such as a clearinghouse acceptance report, payer acknowledgment or EDI confirmation dated within the contracted filing window. If you find that proof, submit a reconsideration request with it through the Copperleaf provider portal within 60 days of the denial date. If you don't, adjust the balance off as a timely filing write-off under the contract terms instead of billing the patient.

OK   fresh-05 (Bramblecrest Insurance): expected policy None, cited None; candidates ['pol-04', 'pol-05']
     category eligibility_or_coverage (label eligibility_or_coverage); no tool call
     next step: Run a real-time eligibility check for the patient on the service date, and ask the patient or employer whether coverage was extended, reinstated (for example through COBRA), or replaced by another plan. If you find active coverage elsewhere, update the registration and bill the correct payer. If you confirm there was no coverage on the service date, move the balance to patient responsibility and send the patient a statement explaining the coverage termination (CARC 27).

OK   fresh-06 (Quillfield Health): expected policy None, cited None; candidates ['pol-08', 'pol-07']
     category duplicate_claim (label duplicate_claim); no tool call
     next step: Check that Q-57191 was paid correctly for this service date and billed service. If it was, close Q-57192 as a duplicate and do not resubmit it, so the same claim line isn't paid twice. If you find an error in the original Q-57191 submission, fix it through the corrected-claim process for Q-57191 rather than sending a new claim.

OK   fresh-07 (Copperleaf Health Plan): expected policy None, cited None; candidates ['pol-01', 'pol-02']
     category eligibility_or_coverage (label eligibility_or_coverage); no tool call
     next step: Check the patient's coverage for the date of service with both Copperleaf Health Plan and the other payer listed, and update the patient's coordination-of-benefits information to show the correct payer order. If the other payer is primary, bill that payer first, then send the claim to Copperleaf as secondary with the primary payer's remittance/EOB attached. If Copperleaf is actually primary (for example, the other coverage had ended or does not apply), resubmit with documentation proving that, such as the other plan's termination letter or the COB exception that applies.

OK   fresh-08 (Quillfield Health): expected policy None, cited None; candidates ['pol-07', 'pol-08']
     category other_or_unclear (label other_or_unclear); tool called, deadline 45 days (matches file)
     next step: Ask Quillfield Health in writing for a written determination on claim Q-90835, as the rep advised, that gives the specific CARC/adjustment reason and the requirement that was not met. Note in the file that timely filing, coverage dates and authorization limits were already confirmed as not the cause. Track the deadline while you wait: if the written determination doesn't arrive in time or shows the denial was wrong, file a reconsideration/appeal through the Quillfield provider portal within 45 days of the denial date.

8 of 8 citations correct (claude-opus-5-5, C:\Users\thein\Documents\fresh-notes.json)
  cited the right snippet: 0 of 0
  correctly cited none: 8 of 8
  citations outside the candidates: 0
  tool called on 4 notes; deadline matched the file on 4
  steps that mention an appeal without a deadline lookup (check by hand): 0
  classifier category correct: 8 of 8
tokens in: 28416, out: 3821, estimated cost: $0.1901, time: 67s
```

Each run also printed the three review questions from `eval_draft.py`:

1. Is the next step right for the denial's actual cause?
2. Does it avoid payer rules that are not in the cited snippet or the tool result?
3. Could a billing specialist act on it as written?
