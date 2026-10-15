import copy
import json
import unittest
from preflight import check

class PolicyTests(unittest.TestCase):
    def setUp(self):
        with open('deployment-pass.json') as f: self.good=json.load(f)
    def codes(self, doc): return {f['code'] for f in check(doc)}
    def test_pass(self): self.assertEqual(check(self.good),[])
    def test_bad_fixture(self):
        with open('deployment-fail.json') as f: bad=json.load(f)
        self.assertEqual(self.codes(bad),{'REPLICAS','IMAGE_PIN','PROBE'})
    def test_registry_port_does_not_count_as_tag(self):
        self.good['spec']['template']['spec']['containers'][0]['image']='localhost:5000/app'
        self.assertIn('IMAGE_PIN',self.codes(self.good))
    def test_selector_mismatch(self):
        self.good['spec']['selector']['matchLabels']['app']='other'
        self.assertIn('SELECTOR',self.codes(self.good))
    def test_privileged_container(self):
        self.good['spec']['template']['spec']['containers'][0]['securityContext']['privileged']=True
        self.assertIn('PRIVILEGED',self.codes(self.good))
    def test_empty_containers(self):
        self.good['spec']['template']['spec']['containers']=[]
        self.assertIn('CONTAINERS',self.codes(self.good))
    def test_empty_digest_is_rejected(self):
        self.good['spec']['template']['spec']['containers'][0]['image']='example/app@sha256:'
        self.assertIn('IMAGE_PIN', self.codes(self.good))
    def test_nonhex_digest_is_rejected(self):
        self.good['spec']['template']['spec']['containers'][0]['image']='example/app@sha256:'+'z'*64
        self.assertIn('IMAGE_PIN', self.codes(self.good))
    def test_valid_digest_passes(self):
        self.good['spec']['template']['spec']['containers'][0]['image']='example/app@sha256:'+'a'*64
        self.assertNotIn('IMAGE_PIN', self.codes(self.good))
    def test_empty_tag_is_rejected(self):
        self.good['spec']['template']['spec']['containers'][0]['image']='example/app:'
        self.assertIn('IMAGE_PIN', self.codes(self.good))
    def test_wrong_kind(self):
        with self.assertRaises(ValueError): check({'kind':'Service'})
    def test_input_is_not_mutated(self):
        before=copy.deepcopy(self.good);check(self.good);self.assertEqual(self.good,before)

if __name__=='__main__': unittest.main()
