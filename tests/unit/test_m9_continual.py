from app.m9.continual import ContinualLearningEngine, LearningEvent, CurriculumScheduler

def test_online_update_and_importance():
    e=ContinualLearningEngine(); e.update(LearningEvent('x',10,1)); assert e.state['x']>0
    old=e.state['x']; e.update(LearningEvent('x',0,.1)); assert e.state['x']>old*.7

def test_consolidate_and_rollback():
    e=ContinualLearningEngine(); e.update(LearningEvent('x',10,1)); e.consolidate(); e.update(LearningEvent('x',20,1)); assert e.rollback(); assert e.state['x']<20

def test_curriculum_adapts():
    c=CurriculumScheduler(.5,.1,1); assert c.update(.9)==.6; assert c.update(.1)==.5
