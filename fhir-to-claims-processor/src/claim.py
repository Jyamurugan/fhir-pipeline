import json
import logging
from fhir.resources.R4B.bundle import Bundle
from fhir.resources.R4B.claim import Claim
from fhir.resources.R4B.patient import Patient

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def process_fhir_bundle(fhir_bundle: str) -> list[dict]:
    try:
        bundle = Bundle.model_validate_json(json.dumps(fhir_bundle))
    except Exception as e:
        logger.error(f"Failed to parse FHIR bundle: {e}")
        return

    patient = None
    for entry in bundle.entry:
        if entry.resource.__resource_type__ == "Patient":
            patient = entry.resource
            break

    if not patient:
        logger.warning("No Patient resource found in the bundle")
        return

    claims: list[dict] = []
    for entry in bundle.entry:
        if entry.resource.__resource_type__ == "Claim":
            try:
                claims.append(process_claims(entry.resource, patient))
            except Exception as e:
                logger.error(f"Failed to process claim: {e}")

    return claims

def process_claims(claim: Claim, patient: Patient) -> dict:
    try:
        claim_id = claim.id
        patient_key = patient.name[0].text if patient.name else None
        billable_period_start = claim.billablePeriod.start if claim.billablePeriod else None
        billable_period_end = claim.billablePeriod.end if claim.billablePeriod else None
        provider = claim.provider.display if claim.provider else None
        facility = claim.facility.display if claim.facility else None

        primary_insurer = None
        secondary_insurer = None
        for insurance in claim.insurance:
            if insurance.sequence == 1:
                primary_insurer = insurance.coverage.display
            else:
                secondary_insurer = insurance.coverage.display

        primary_diagnosis_key = None
        for diagnosis in claim.diagnosis:
            if diagnosis.sequence == 1:
                primary_diagnosis_key = diagnosis.diagnosisCodeableConcept.coding[0].code
                break

        product_or_service = None
        for item in claim.item:
            if item.sequence == 1:
                product_or_service = item.productOrService.text
                break

        return {
            "claim_id": claim_id,
            "patient_key": patient_key,
            "billable_period_start": billable_period_start,
            "billable_period_end": billable_period_end,
            "provider_key": provider,
            "facility_key": facility,
            "primary_insurer": primary_insurer,
            "secondary_insurer": secondary_insurer,
            "primary_diagnosis": primary_diagnosis_key,
            "product_or_service": product_or_service,
            "net": item.net.amount if item.net else 0
        }
    except Exception as e:
        logger.error(f"Error processing claim: {e}")
        raise