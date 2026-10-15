# Validation

Local validation on Python 3.9.6.

## Unit tests

```text
test_bad_fixture (test_preflight.PolicyTests) ... ok
test_empty_containers (test_preflight.PolicyTests) ... ok
test_empty_digest_is_rejected (test_preflight.PolicyTests) ... ok
test_empty_tag_is_rejected (test_preflight.PolicyTests) ... ok
test_input_is_not_mutated (test_preflight.PolicyTests) ... ok
test_nonhex_digest_is_rejected (test_preflight.PolicyTests) ... ok
test_pass (test_preflight.PolicyTests) ... ok
test_privileged_container (test_preflight.PolicyTests) ... ok
test_registry_port_does_not_count_as_tag (test_preflight.PolicyTests) ... ok
test_selector_mismatch (test_preflight.PolicyTests) ... ok
test_valid_digest_passes (test_preflight.PolicyTests) ... ok
test_wrong_kind (test_preflight.PolicyTests) ... ok

----------------------------------------------------------------------
Ran 12 tests in 0.001s

OK
```

## python3 preflight.py deployment-pass.json

Exit status: 0

```json
{
  "passed": true,
  "findings": []
}
```

## python3 preflight.py deployment-fail.json

Exit status: 1

```json
{
  "passed": false,
  "findings": [
    {
      "code": "REPLICAS",
      "path": "spec.replicas",
      "message": "Use at least two replicas for this availability policy."
    },
    {
      "code": "IMAGE_PIN",
      "path": "spec.template.spec.containers[0].image",
      "message": "Use a nonempty version tag or a valid SHA-256 image digest."
    },
    {
      "code": "PROBE",
      "path": "spec.template.spec.containers[0].readinessProbe",
      "message": "Configure a probe handler."
    }
  ]
}
```

These checks use small synthetic fixtures. They do not establish production readiness or cloud deployment results.
