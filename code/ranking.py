#!/usr/bin/env python
import random
from density import margin_density, similarityMatrix, margin_k_density, density, k_density

def margin_distance(classifier, f, classes=["RELATED", "UNRELATED"]):
    pdist = classifier.prob_classify(f[0])
    distance = abs(pdist.prob(classes[0])-pdist.prob(classes[1]))
    return distance

def reranker(samples, topX, rerank_method, testfeatures=[], similarity_matrix=[], id2row=[], K=5):
    cutoff = int(topX*len(samples)+0.5)
    if K:
      return sorted(samples[:cutoff], key=lambda x:k_density(similarity_matrix,
             id2row[x[1]], K), reverse=True)
    return sorted(samples[:cutoff], key=lambda x:density(similarity_matrix,
            id2row[x[1]]), reverse=True)

def ranks(classifier,
          testfeatures,
          sampling="margin",
          rerank = False,
          params = {'topX': 0.2},
          classes=["RELATED", "UNRELATED"]):
    samples = []
    if sampling == "margin_density":
        similarity_matrix = params['simmatrix']
        id2row = params['id2row']
    for k,f in testfeatures.iteritems():
        ranking_value = 0
        if sampling in ["margin", "margin_density"]:
           distance = margin_distance(classifier, f, classes)
           ranking_value = distance
        if sampling == "margin_density":
            if "K" in params:
               ranking_value = margin_k_density(distance,
                               similarity_matrix,
                               id2row[k], params["K"])
            else:
                ranking_value = margin_density(distance,
                    similarity_matrix,
                    id2row[k])
        samples.append((ranking_value, k))

    random.shuffle(samples)
    if sampling in ["margin", "margin_density"]:
       samples.sort()
    if rerank:
       return reranker(samples, params["topX"], params['reranker'], testfeatures=testfeatures, similarity_matrix=params.get('simmatrix', []), id2row=params.get('id2row', []), K=params.get('K', None))
    return samples

def main():
  pass

if __name__ == '__main__':
  main()
