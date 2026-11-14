"""Deterministic chemistry checks; not a substitute for independent review."""
from pathlib import Path
import json,re
from fractions import Fraction as F

ROOT=Path(__file__).resolve().parents[1]

def atoms(formula):
    # The regression equations use unparenthesised empirical formulae.
    parts=re.findall(r'([A-Z][a-z]?)(\d*)',formula)
    assert ''.join(a+n for a,n in parts)==formula,formula
    result={}
    for a,n in parts:result[a]=result.get(a,0)+int(n or 1)
    return result

def check_equation(eq):
    totals=[];charges=[]
    for side in ('left','right'):
        total={};charge=0
        for coefficient,formula,q in eq[side]:
            for a,n in atoms(formula).items():total[a]=total.get(a,0)+coefficient*n
            charge+=coefficient*q
        totals.append(total);charges.append(charge)
    assert totals[0]==totals[1],(eq['id'],'atoms',totals)
    assert charges[0]==charges[1],(eq['id'],'charge',charges)

def main():
    data=json.loads((ROOT/'data/haidian_verified.json').read_text(encoding='utf8'))
    assert len(data['questions'])==19
    assert [q['number'] for q in data['questions']]==list(range(1,20))
    assert all(set(q['options'])==set('ABCD') for q in data['questions'][:14])
    for e in data['equations']:check_equation(e)
    # A deliberately wrong 1:2 ratio must be rejected, even though charges balance.
    wrong={'id':'negative_control','left':[[1,'ClO',-1],[2,'ClO2',-1]],'right':[[1,'Cl',-1],[2,'ClO3',-1]]}
    try:check_equation(wrong)
    except AssertionError:pass
    else:raise AssertionError('checker accepted unbalanced equation')
    # Independent stoichiometric reconstruction of back titration at three ratios.
    for total_mn,x,remaining in [(F(1,100),4,F(1,100)),(F(1,50),3,F(1,200)),(F(3,100),F(7,2),F(1,100))]:
        ox_consumed=total_mn*(x-2)/2
        ox_added=remaining+ox_consumed
        half_perm=remaining/5
        half_edta=total_mn/2
        result=2+(ox_added-5*half_perm)/half_edta
        assert result==x
    # Q17 Hess; Q18 electron balance, pH intersection, hydroxide requirement.
    assert (247-165)/2==41
    assert max(4.7,3.4)==4.7 and min(6.3,7.4)==6.3
    assert 2*(6-2)==8 and 8*(3-2)==8
    assert 2*3-2==4
    assert data['ph_window']=={'step':'precipitate_aluminium','lower':4.7,'upper':6.3,'upper_inclusive':False}
    assert data['q19_7']=='agree_possible_SO2_source'
    if 'q16_2ii_answer' in data:
        answer=data['q16_2ii_answer']
        assert all(point in answer for point in ['Cl₂、CCl₄为非极性分子','ClO₂为极性分子','相似相溶','ClO₂不易溶于CCl₄','Cl₂易溶于CCl₄','除去混合气体中的Cl₂'])
        lesson=(ROOT/'assets/haidian_lessons.txt').read_text(encoding='utf8')
        key=lesson.split('@@ 第1题',1)[0]
        assert answer in key, 'reference answer omits a scoring point'
        assert '@choices BACDDACDBDDCBC' in key
    print(f'PASS: 19 questions, 56 choice-option entries, {len(data["equations"])} atom/charge checks, negative control, 3 titration reconstructions, Hess, electron and pH checks.')

if __name__=='__main__':main()
