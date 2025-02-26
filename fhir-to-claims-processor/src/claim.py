import decimal
import json
import logging
from fhir.resources.R4B.bundle import Bundle
from fhir.resources.R4B.claim import Claim
from fhir.resources.R4B.condition import Condition
from fhir.resources.R4B.patient import Patient
from datetime import datetime

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ProcessedClaim:
    def __init__(self, claim_id: str, patient_key: str, billable_period_start: datetime, billable_period_end: datetime, provider_key: str, facility_key: str, primary_insurer: str, secondary_insurer: str, primary_diagnosis: str, product_or_service: str, net: float, currency: str) -> None:
        self.claim_id = claim_id
        self.patient_key = patient_key
        self.billable_period_start = billable_period_start
        self.billable_period_end = billable_period_end
        self.provider_key = provider_key
        self.facility_key = facility_key
        self.primary_insurer = primary_insurer
        self.secondary_insurer = secondary_insurer
        self.primary_diagnosis = primary_diagnosis
        self.product_or_service = product_or_service
        self.net = net
        self.currency = currency

    def __repr__(self) -> str:
                return json.dumps(self.__dict__)

    def toJSON(self):
        def default_converter(o):
            if isinstance(o, datetime):
                return o.isoformat()
            if isinstance(o, decimal.Decimal):
                return f"{o:.2f}"
            return o.__dict__
        return json.dumps(self, default=default_converter, sort_keys=True)

def process_fhir_bundle(fhir_bundle: str) -> list[ProcessedClaim]:
    try:
        bundle = Bundle.model_validate_json(fhir_bundle)
    except Exception as e:
        logger.error(f"Failed to parse FHIR bundle: {e}")
        raise

    patient = None
    processed_claims: list[dict] = []
    claims: list[Claim] = []
    conditions: list[Condition] = []
    for entry in bundle.entry:
        if entry.resource.__resource_type__ == "Claim":
            claims.append(entry.resource)
        if entry.resource.__resource_type__ == "Condition":
            conditions.append(entry.resource)
        if entry.resource.__resource_type__ == "Patient":
            patient = entry.resource
    
    if not patient:
        error_message = "No Patient resource found in the bundle"
        logger.error(error_message)
        raise ValueError(error_message)
    
    for claim in claims:
        try:
            processed_claims.append(process_claims(claim, patient, conditions))
        except Exception as e:
            logger.error(f"Failed to process claim: {e}")
            raise

    return processed_claims

def process_claims(claim: Claim, patient: Patient, conditions: list[Condition]) -> ProcessedClaim:
    try:
        claim_id = claim.id
        patient_key = patient.id
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
        if claim.diagnosis:
            for diagnosis in claim.diagnosis:
                if diagnosis.sequence == 1 and diagnosis.diagnosisReference:            
                    primary_diagnosis_key = next((condition.code.text for condition in conditions if ("urn:uuid:"+ condition.id) == diagnosis.diagnosisReference.reference), None)
                    break

        product_or_service = None
        for item in claim.item:
            if item.sequence == 1:
                product_or_service = item.productOrService.text
                break

        processed_claim = ProcessedClaim(
            claim_id=claim_id,
            patient_key=patient_key,
            billable_period_start=billable_period_start,
            billable_period_end=billable_period_end,
            provider_key=provider,
            facility_key=facility,
            primary_insurer=primary_insurer,
            secondary_insurer=secondary_insurer,
            primary_diagnosis=primary_diagnosis_key,
            product_or_service=product_or_service,
            net=claim.total.value if claim.total else 0,
            currency= claim.total.currency if claim.total else None
        )
        return processed_claim
    except Exception as e:
        logger.error(f"Error processing claim: {e}")
        raise