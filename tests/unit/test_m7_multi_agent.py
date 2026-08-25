from app.m7.multi_agent import LeagueManager, MatchResult, OpponentModel, PolicyEvaluator, MultiAgentPlanner, SelfPlayEvolution, EvolutionConfig

def test_league_updates_ratings():
    l=LeagueManager(); l.register('a'); l.register('b')
    l.record(MatchResult('a','b'))
    assert l.agents['a'].rating > 1000 and l.agents['b'].rating < 1000

def test_leaderboard_orders_strength():
    l=LeagueManager(); l.register('a'); l.register('b'); l.record(MatchResult('a','b'))
    assert l.leaderboard()[0].agent_id == 'a'

def test_opponent_profile_confidence_grows():
    p=OpponentModel().profile('x',[{'aggression':.8,'variance':.1,'rating':1100}]*10)
    assert p.aggression == .8 and p.confidence == .5

def test_policy_evaluator():
    e=PolicyEvaluator(); rows=[MatchResult('a','b'),MatchResult(None,None,True)]
    assert e.score(rows,'a') == .75

def test_multi_agent_planner_adjusts_scores():
    p=OpponentModel().profile('x',[{'aggression':1,'variance':0,'rating':1100}])
    out=__import__('app.m7.multi_agent',fromlist=['MultiAgentPlanner']).MultiAgentPlanner().adjust({'a':1},p)
    assert out['a'] > 1

def test_draw_updates_both_ratings_and_counts():
    l=LeagueManager(); l.register('a'); l.register('b')
    l.record(MatchResult('a','b',True))
    assert l.agents['a'].draws == l.agents['b'].draws == 1
    assert l.agents['a'].rating == l.agents['b'].rating == 1000.0


def test_lifecycle_and_policy_versioning():
    l=LeagueManager(); l.register('a', policy={'x':1}, policy_version=2)
    l.update_policy('a', {'x':2})
    assert l.agents['a'].policy_version == 3
    l.retire('a'); assert l.agents['a'].status == 'retired'
    l.activate('a'); assert l.agents['a'].status == 'active'


def test_balanced_opponent_selection_prefers_closest_rating():
    l=LeagueManager(); l.register('a'); l.register('b'); l.register('c')
    l.agents['b'].rating = 1010
    l.agents['c'].rating = 1300
    assert l.select_opponents('a')[0].agent_id == 'b'


def test_challenger_promotion_requires_games_and_rating_gap():
    l=LeagueManager(promotion_delta=300, min_games_for_promotion=2)
    l.register('champ'); l.register('challenger')
    l.agents['champ'].rating = 1000
    l.agents['challenger'].rating = 1120
    assert not l.promote_challenger('challenger')
    for _ in range(2):
        l.record(MatchResult('challenger','champ'))
    l.agents['challenger'].rating = 1400
    assert l.promote_challenger('challenger')
    assert l.champion().agent_id == 'challenger'
    assert l.agents['champ'].status == 'challenger'


def test_underplayed_selection_is_fair():
    l=LeagueManager(); [l.register(x) for x in ('a','b','c')]
    l.record(MatchResult('a','b'))
    assert l.select_opponents('c', strategy='underplayed')[0].agent_id == 'a'


def test_snapshot_round_trip(tmp_path):
    path=tmp_path/'league.json'
    l=LeagueManager(); l.register('a', policy={'name':'a'}, policy_version=4); l.register('b')
    l.record(MatchResult('a','b'))
    l.save(path)
    restored=LeagueManager.load(path)
    assert restored.champion().agent_id == l.champion().agent_id
    assert restored.agents['a'].games == 1
    assert restored.agents['a'].policy_version == 4


def test_unknown_participant_is_rejected():
    l=LeagueManager(); l.register('a')
    try:
        l.record(MatchResult('a','missing'))
    except KeyError:
        pass
    else:
        raise AssertionError('missing participant should raise')


def test_challenger_can_be_demoted_when_far_below_champion():
    l=LeagueManager(demotion_delta=100, min_games_for_promotion=2)
    l.register('champ'); l.register('challenger')
    l.agents['challenger'].status = 'challenger'
    l.agents['challenger'].matches = 2
    l.agents['challenger'].wins = 2
    l.agents['challenger'].rating = 700
    assert l.demote_if_needed('challenger')
    assert l.agents['challenger'].demotions == 1


def test_opponent_model_online_observation_and_prediction():
    model=OpponentModel(decay=0.5)
    model.observe('x', {'aggression': .2, 'variance': .1, 'rating': 1000})
    model.observe('x', {'aggression': .9, 'variance': .2, 'rating': 1200})
    prediction=model.predict('x')
    assert prediction['aggression'] > .5
    assert prediction['strength'] > 1000
    assert 0 < prediction['confidence'] < 1


def test_opponent_model_reset_removes_learned_behavior():
    model=OpponentModel(); model.observe('x', {'aggression': 1.0})
    assert model.history('x')
    model.reset('x')
    assert model.history('x') == []
    assert model.profile('x').confidence == 0.0


def test_self_play_evolution_creates_versioned_offspring():
    league=LeagueManager()
    evolution=SelfPlayEvolution(league, EvolutionConfig(population_size=3, elite_count=1, generations=1))
    evolution.seed({'a': {'score': 1}, 'b': {'score': 0}, 'c': {'score': 0}})
    def play_generation(agents):
        return [MatchResult('a','b'), MatchResult('a','c')]
    def mutate(policy, rate, index):
        return {'score': policy['score'] + index, 'rate': rate}
    ranked=evolution.evolve(mutate, play_generation)
    assert ranked[0].agent_id == 'a'
    assert any(':g2:' in agent.agent_id for agent in league.agents.values())
    assert all(agent.policy_version >= 2 for agent in league.agents.values() if ':g2:' in agent.agent_id)


def test_multi_agent_planner_integrates_opponent_model_and_risk():
    from app.m7.multi_agent import MultiAgentAction
    model = OpponentModel()
    model.observe_many('enemy', [
        {'aggression': 0.9, 'variance': 0.1, 'rating': 1200},
        {'aggression': 0.9, 'variance': 0.1, 'rating': 1200},
    ])
    planner = MultiAgentPlanner(model)
    result = planner.plan([
        MultiAgentAction('safe_counter', base_score=1.0, matchup_score=0.8, risk=0.1, information_gain=0.2),
        MultiAgentAction('high_damage', base_score=1.1, matchup_score=0.2, risk=0.9, information_gain=0.0),
    ], opponent_id='enemy')
    assert result.action_id == 'safe_counter'
    assert result.opponent_confidence > 0


def test_multi_agent_planner_uses_league_evaluation_confidence():
    from app.m7.multi_agent import MultiAgentAction
    league = LeagueManager()
    league.register('self')
    league.register('enemy')
    league.record(MatchResult('self', 'enemy'))
    planner = MultiAgentPlanner(league=league)
    result = planner.plan([
        MultiAgentAction('a', 1.0, matchup_score=0.1, risk=0.1),
        MultiAgentAction('b', 0.9, matchup_score=0.8, risk=0.1),
    ], opponent_id='enemy', agent_id='self')
    assert result.action_id in {'a', 'b'}
    assert 'evaluation_confidence=' in result.rationale


def test_multi_agent_planner_rejects_empty_actions():
    planner = MultiAgentPlanner()
    try:
        planner.plan([], opponent_id='enemy')
    except ValueError:
        pass
    else:
        raise AssertionError('empty action set should raise')
