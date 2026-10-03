"""Independent reviewer answer key; never import this into the generator."""
import json
import math
from pathlib import Path


def batch_norm(x, gamma=1.0, beta=0.0):
    mean = sum(x) / len(x)
    variance = sum((v - mean) ** 2 for v in x) / len(x)
    normalized = [(v - mean) / math.sqrt(variance + 1e-5) for v in x]
    return dict(mean=mean, variance=variance, normalized=normalized,
                y=[gamma * v + beta for v in normalized])


def gaussian_kl(mu, sigma):
    terms = [0.5 * (m*m + s*s - 1 - math.log(s*s)) for m, s in zip(mu, sigma)]
    return dict(per_coordinate=terms, total=sum(terms))


def focal(p_t, gamma, scale=1.0):
    ce = -math.log(p_t)
    modulation = (1-p_t) ** gamma
    return dict(cross_entropy=ce, modulation=modulation,
                focal_loss=ce*modulation, demonstration_loss=scale*ce*modulation)


def adam(gradients, alpha, steps):
    theta, m, v = 1.0, 0.0, 0.0
    history = []
    for t, gradient in enumerate(gradients[:steps], 1):
        m = 0.9*m + 0.1*gradient
        v = 0.999*v + 0.001*gradient*gradient
        mhat, vhat = m/(1-0.9**t), v/(1-0.999**t)
        delta = alpha*mhat/(math.sqrt(vhat)+1e-8)
        theta -= delta
        history.append(dict(step=t, m=m, v=v, mhat=mhat, vhat=vhat,
                            subtracted_update=delta, theta=theta))
    return dict(history=history, theta=theta)


def attention(Q, K, V, scaling):
    raw = [[sum(a*b for a,b in zip(q,k)) for k in K] for q in Q]
    divisor = math.sqrt(len(Q[0])) if scaling else 1.0
    scores = [[x/divisor for x in row] for row in raw]
    weights = []
    for row in scores:
        exps = [math.exp(x-max(row)) for x in row]
        weights.append([x/sum(exps) for x in exps])
    output = [[sum(row[j]*V[j][c] for j in range(len(K)))
               for c in range(len(V[0]))] for row in weights]
    return dict(raw_scores=raw, scores=scores, weights=weights, output=output)


def entropy(weights, n):
    active = weights[:n]
    total = sum(active)
    probabilities = [x/total for x in active] if total else [1/n]*n
    terms = [-x*math.log2(x) if x else 0.0 for x in probabilities]
    return dict(probabilities=probabilities, contributions_bits=terms,
                entropy_bits=sum(terms), uniform_fallback=(total == 0))


def build():
    result = {}
    def add(case, name, inputs, output):
        result.setdefault(case, []).append(dict(probe=name, inputs=inputs, expected=output))
    for name, x, g, b in [('default',[1,2,3,4],1,0),('constant',[3,3,3,3],2,-1),('negative_scale',[1,2,3,4],-2,1)]:
        add('01_batch_norm',name,dict(x=x,gamma=g,beta=b),batch_norm(x,g,b))
    for name,mu,sigma in [('default',[1,0],[1,2]),('match_prior',[0,0],[1,1]),('shift_mean',[2,0],[1,1]),('small_sigma',[0,0],[0.1,1])]:
        add('02_gaussian_kl',name,dict(mu=mu,sigma=sigma),gaussian_kl(mu,sigma))
    for name,pt,g in [('default',0.9,2),('gamma_zero',0.9,0),('difficult',0.1,2),('balanced',0.5,2)]:
        add('03_focal_loss',name,dict(p_t=pt,gamma=g),focal(pt,g))
        add('07_offline_unknown_field',name,dict(p_t=pt,gamma=g),focal(pt,g,3.7))
    for name,gs,alpha,steps in [('default',[2,2,2],0.1,1),('negative',[-2,-2,-2],0.1,1),('zero',[0,0,0],0.1,3),('two_steps',[2,2,2],0.1,2),('reversal',[2,-2,2],0.1,2),('no_update',[2,2,2],0,3)]:
        add('04_adam',name,dict(gradients=gs,alpha=alpha,steps=steps),adam(gs,alpha,steps))
    K=[[1,0],[0,1]]; V=[[10],[20]]
    for name,Q,scaling in [('default',K,True),('unscaled',K,False),('equal_scores',[[0,0],[0,0]],True),('large',[[1000,0],[0,1000]],True)]:
        add('05_attention_stability',name,dict(Q=Q,K=K,V=V,scaling=scaling),attention(Q,K,V,scaling))
    for name,w,n in [('default',[1,1,1,1],4),('certainty',[1,0,0,0],4),('three_outcomes',[1,1,1,1],3),('one_outcome',[1,1,1,1],1),('all_zero',[0,0,0,0],4),('zero_active_prefix',[0,0,1,1],2)]:
        add('06_entropy_edges',name,dict(weights=w,n=n),entropy(w,n))
    return result


def verify_reference():
    assert batch_norm([3,3,3,3],2,-1)['y'] == [-1]*4
    assert batch_norm([1,2,3,4])['variance'] == 1.25
    assert gaussian_kl([0,0],[1,1])['total'] == 0
    assert gaussian_kl([2,0],[1,1])['total'] == 2
    assert math.isclose(focal(0.5,2)['focal_loss'],math.log(2)/4,rel_tol=1e-12)
    assert math.isclose(adam([2,2,2],0.1,1)['theta'],1-0.2/(2+1e-8),abs_tol=1e-12)
    assert adam([0,0,0],0.1,3)['theta'] == 1
    assert attention([[0,0],[0,0]],[[1,0],[0,1]],[[10],[20]],True)['output'] == [[15],[15]]
    for row in attention([[1000,0],[0,1000]],[[1,0],[0,1]],[[10],[20]],True)['weights']:
        assert math.isclose(sum(row),1,abs_tol=1e-12) and all(math.isfinite(x) for x in row)
    assert entropy([1,1,1,1],4)['entropy_bits'] == 2
    assert entropy([1,0,0,0],4)['entropy_bits'] == 0
    assert entropy([0,0,1,1],2)['probabilities'] == [0.5,0.5]


if __name__ == '__main__':
    verify_reference()
    target=Path(__file__).with_name('expected_results.json')
    target.write_text(json.dumps(build(),indent=2,allow_nan=False)+'\n',encoding='utf-8')
    print('Reference identities verified; wrote',target.name)
