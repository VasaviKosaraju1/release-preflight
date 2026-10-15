"""Check Kubernetes Deployment JSON before a release. No cluster access required."""
import argparse
import json
from pathlib import Path
import sys


def check(document):
    if not isinstance(document, dict) or document.get('kind') != 'Deployment':
        raise ValueError('expected a Kubernetes Deployment object')
    findings = []
    def report(code, path, message):
        findings.append({'code': code, 'path': path, 'message': message})
    spec = document.get('spec', {})
    replicas = spec.get('replicas', 1)
    if isinstance(replicas, bool) or not isinstance(replicas, int) or replicas < 2:
        report('REPLICAS', 'spec.replicas', 'Use at least two replicas for this availability policy.')
    template = spec.get('template', {})
    selector = spec.get('selector', {}).get('matchLabels', {})
    labels = template.get('metadata', {}).get('labels', {})
    if not selector or any(labels.get(k) != v for k,v in selector.items()):
        report('SELECTOR', 'spec.selector.matchLabels', 'Selector must match pod template labels.')
    pod = template.get('spec', {})
    pod_security = pod.get('securityContext', {})
    if pod.get('hostNetwork') or pod.get('hostPID') or pod.get('hostIPC'):
        report('HOST_ACCESS', 'spec.template.spec', 'Host namespace sharing is disallowed.')
    containers = pod.get('containers', [])
    if not containers:
        report('CONTAINERS', 'spec.template.spec.containers', 'At least one container is required.')
    for position, container in enumerate(containers):
        path = f'spec.template.spec.containers[{position}]'
        image = container.get('image', '')
        tail = image.rsplit('/', 1)[-1]
        if not image or (not '@sha256:' in image and (':' not in tail or tail.endswith(':latest'))):
            report('IMAGE_PIN', path+'.image', 'Use an explicit version tag or image digest.')
        for group in ('requests', 'limits'):
            values = container.get('resources', {}).get(group, {})
            if any(not values.get(key) for key in ('cpu', 'memory')):
                report('RESOURCES', path+'.resources.'+group, 'Set CPU and memory '+group+'.')
        for probe in ('readinessProbe', 'livenessProbe'):
            config = container.get(probe, {})
            if not any(key in config for key in ('httpGet','tcpSocket','exec','grpc')):
                report('PROBE', path+'.'+probe, 'Configure a probe handler.')
        security = {**pod_security, **container.get('securityContext', {})}
        if security.get('runAsNonRoot') is not True:
            report('NON_ROOT', path+'.securityContext', 'Require runAsNonRoot.')
        if security.get('allowPrivilegeEscalation') is not False:
            report('ESCALATION', path+'.securityContext', 'Disable privilege escalation.')
        if security.get('privileged') is True:
            report('PRIVILEGED', path+'.securityContext', 'Privileged containers are disallowed.')
        if security.get('readOnlyRootFilesystem') is not True:
            report('ROOT_FS', path+'.securityContext', 'Use a read-only root filesystem.')
    return findings


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('manifest')
    args=parser.parse_args()
    try:
        findings=check(json.loads(Path(args.manifest).read_text()))
    except (OSError, ValueError, TypeError, AttributeError) as error:
        print(json.dumps({'error':str(error)}), file=sys.stderr)
        return 2
    print(json.dumps({'passed':not findings,'findings':findings},indent=2))
    return 1 if findings else 0

if __name__=='__main__': sys.exit(main())
