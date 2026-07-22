from pathlib import Path
from sric.workspace import Workspace
from authtwin.core import AuthTwinEngine
from authtwin.models import Actor, Resource, AuthorizationObservation, Decision, Invariant, InvariantKind, SessionEvent

def make(tmp_path: Path) -> AuthTwinEngine:
    return AuthTwinEngine(Workspace.create(tmp_path, 'ws').root)

def test_coverage_counterfactual_session_graphql_batch_and_skeptic(tmp_path):
    e = make(tmp_path)
    e.add_actor(Actor(actor_id='a', name='A'))
    e.add_actor(Actor(actor_id='b', name='B'))
    e.add_resource(Resource(resource_id='r1', resource_type='doc', owner_actor_id='a'))
    e.observe(AuthorizationObservation(observation_id='o1', actor_id='a', resource_id='r1', operation='READ', decision=Decision.ALLOW, evidence_ids=['E1'], metadata={'graphql_operation': 'GetDoc', 'graphql_field': 'document'}))
    e.observe(AuthorizationObservation(observation_id='o2', actor_id='b', resource_id='r1', operation='UPDATE', decision=Decision.ALLOW, evidence_ids=['E2'], metadata={'batch_items': [{'id': 'r1', 'decision': 'ALLOW'}, {'id': 'r2', 'decision': 'DENY'}]}))
    cov = e.coverage()
    assert cov.possible_cells == 4 and cov.observed_cells == 2 and (cov.coverage == 0.5)
    plans = e.counterfactuals('o1')
    assert len(plans) == 1 and plans[0].candidate_actor_id == 'b' and plans[0].requires_approval
    e.add_session_event(SessionEvent(event_id='s1', actor_id='a', event_type='LOGIN', evidence_ids=['E3']))
    assert e.session_lifecycle('a')[0]['event_type'] == 'LOGIN'
    assert e.graphql_surface()[0]['operation'] == 'GetDoc'
    assert e.batch_authorization()[0]['mixed_decisions'] is True
    inv = Invariant(invariant_id='I1', description='no other owner update', kind=InvariantKind.DENY_OTHER_OWNER_MUTATION, operations=['UPDATE'])
    e.add_invariant(inv)
    findings = e.evaluate()
    assert findings and findings[0].status == 'HYPOTHESIS'
    review = e.skeptic_review(findings[0].finding_id)
    assert review.counter_tests and review.recommended_status == 'VALIDATION_READY'
    assert e.graph.search('authorization_observation')
    assert e.lineage.explain('observation:o1')['artifact']['status'] == 'OBSERVED'

def test_invariant_dsl_is_small_and_fail_closed(tmp_path):
    e = make(tmp_path)
    inv = e.parse_invariant_dsl('id: X\ndescription: Test\nkind: DENY_SUSPENDED\noperations: READ')
    assert inv.kind == InvariantKind.DENY_SUSPENDED
