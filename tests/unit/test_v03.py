from pathlib import Path
from sric.workspace import Workspace
from authtwin.core import AuthTwinEngine
from authtwin.advanced import AuthorizationIntelligence, normalize_endpoint
from authtwin.models import Actor,Resource,AuthorizationObservation,Decision,MembershipEvent


def engine(tmp_path:Path)->AuthTwinEngine:
    return AuthTwinEngine(Workspace.create(tmp_path,'w').root)


def test_endpoint_discovery_binding_and_state_v2(tmp_path):
    e=engine(tmp_path);e.add_actor(Actor(actor_id='A',name='A'));e.add_actor(Actor(actor_id='B',name='B'))
    e.add_resource(Resource(resource_id='R1',resource_type='doc',owner_actor_id='A',tenant='T'))
    e.observe(AuthorizationObservation(observation_id='O1',actor_id='A',resource_id='R1',operation='READ',decision=Decision.ALLOW,evidence_ids=['E1'],metadata={'url':'https://api.example/documents/123456789012','created_resource':True}))
    intel=AuthorizationIntelligence(e);d=intel.discovery_v2();assert d['families'][0]['template']=='/documents/{id1}' and d['ownership_status']=='INFERRED_OR_UNKNOWN'
    bindings=intel.infer_actor_resource_bindings();assert bindings and all(x.status.value=='INFERRED' for x in bindings)
    intel.add_membership_event(MembershipEvent(event_id='M1',actor_id='A',tenant_id='T',state='REMOVED',evidence_ids=['E2']))
    state=intel.state_machine_v2();assert state['membership_events']['A'][0]['state']=='REMOVED'


def test_mutation_plans_are_hypotheses_and_safety_gated(tmp_path):
    e=engine(tmp_path);e.add_actor(Actor(actor_id='A',name='A'));e.add_actor(Actor(actor_id='B',name='B'));e.add_resource(Resource(resource_id='R1',resource_type='doc'));e.add_resource(Resource(resource_id='R2',resource_type='doc'))
    e.observe(AuthorizationObservation(observation_id='O1',actor_id='A',resource_id='R1',operation='READ',decision=Decision.ALLOW,evidence_ids=['E1']))
    plans=AuthorizationIntelligence(e).mutation_plans();assert len(plans)>=2
    assert all(p.status.value=='HYPOTHESIS' and p.requires_scope and p.requires_policy and p.requires_rate_limit and p.requires_approval and p.executor=='reprosec' for p in plans)


def test_differential_invariant_library_and_websocket(tmp_path):
    e=engine(tmp_path);e.add_actor(Actor(actor_id='A',name='A'));e.add_actor(Actor(actor_id='B',name='B'));e.add_resource(Resource(resource_id='R1',resource_type='doc'))
    e.observe(AuthorizationObservation(observation_id='O1',actor_id='A',resource_id='R1',operation='READ',decision=Decision.ALLOW,status_code=200,evidence_ids=['E1'],metadata={'response_fields':['owner','title'],'websocket_subscription':'room:R1','membership_state':'ACTIVE'}))
    e.observe(AuthorizationObservation(observation_id='O2',actor_id='B',resource_id='R1',operation='READ',decision=Decision.DENY,status_code=403,evidence_ids=['E2'],metadata={'response_fields':['title'],'websocket_subscription':'room:R1','membership_state':'REMOVED','revocation_observed':True}))
    intel=AuthorizationIntelligence(e);d=intel.differential_response('O1','O2');assert d.status.value=='HYPOTHESIS' and d.sensitive_differences
    installed=intel.install_invariant_library();assert {'LIB-OWNERSHIP','LIB-TENANT','LIB-REVOCATION'}<=set(installed)
    ws=intel.websocket_surface();assert len(ws)==2 and any(x['revocation_observed'] for x in ws)


def test_normalize_endpoint_is_conservative():
    n=normalize_endpoint('/users/123/resources/abcdef1234567890');assert n['template']=='/users/{id1}/resources/{id2}'
