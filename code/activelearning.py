import nltk, sys, numpy, os
import argparse

from sklearn.svm import SVC
from nltk.classify.decisiontree import DecisionTreeClassifier
from nltk.classify.naivebayes import NaiveBayesClassifier
from nltk.classify.scikitlearn import SklearnClassifier

from util import *
from density import similarityMatrix
from ranking import ranks

def parse():
    "Set up the argument list"
    parser = argparse.ArgumentParser(description=u'Active Learning for Entity Filtering in Microblog Streams.\nDamiano Spina, Maria-Hendrike Peetz and Maarten de Rijke.\nSIGIR\'15, 2015. http://damiano.github.io/al-ef')

    parser.add_argument('-s', metavar="TWEET_CONTENT_FILE_TRAINING", required=True, help='file with the mapping between id an text (training)',)
    parser.add_argument('-S', metavar="TWEET_CONTENT_FILE_TEST", required=True, help='file with the mapping between id an text (test)',)

    parser.add_argument('-st', metavar="STOPWORDS_DIR", required=False, help="Stopword lists' dir (for BoW+presence representation).")
    parser.add_argument('-t', metavar="FEATURE_FILE_TRAINING", required=False, help='features for training. If not provided, BoW+presence represenation is then computed by the script.')
    parser.add_argument('-T', metavar="FEATURE_FILE_TEST", required=False, help='features for testing. If not provided, BoW+presence representation is then computed by the script.')

    parser.add_argument('-g', metavar="GOLDSTANDARD_TRAINING_FILE", required=True,help='Goldstandard for training',)
    parser.add_argument('-G', metavar="GOLDSTANDARD_TEST_FILE", required=True, help='Goldstandard for test (used to simulate active learning)',)

    parser.add_argument('-O', metavar="OUTPUT_ANNOTATION_FILE", help='Outfile for the annotations in the test data.',)
    parser.add_argument('-o', metavar="OUTPUT_CLASSIFICATION_FILE", help='Outfile for the classifications in the test data.',)

    parser.add_argument('-c', type=str, help="NLTK 2.0 Classification algorithm: NaiveBayesClassifier, DecisionTreeClassifier. If not provided scikitlearn.svm.SVC is used.", required=False)
    parser.add_argument('-I', type=int, default=1, help='Number of items to annotate per iteration for the active learning update.')
    parser.add_argument('-w', type=float, default=1, help='Number of times a newly annotated item should be added to the test set. If <1, it will be |training_set|*w')


    parser.add_argument('-sm', type=str, help='Active Learning Sampling mode: random, margin, or margin_density',default="margin")

    parser.add_argument('-K', type=int, default=None, help='K for KNN')

    parser.add_argument('-topX', type=float, default=0, help='Top X percent that will be reranked. If 0, no reranking happens.')

    return parser.parse_args()



def mostDiscriminateSample(classifier,
                           testfeatures,
                           sampling="margin",
                           reranking = False,
                           params = {'topX': 0.2},
                           classes=["RELATED", "UNRELATED"]):
    return ranks(classifier,
                 testfeatures,
                 sampling,
                 reranking,
                 params,
                 classes)

def simulatedActiveAnnotation(sortedAnnotationFeature, id2tweet, goldstandard, limit=2):
    "Simulates tha Active Learning annotation by reading the labels from the goldstandard"
    annotated = []
    for instance in sortedAnnotationFeature[:limit]:
        print instance
        tweetid = instance[1]
        label = goldstandard[long(tweetid)]
        annotated.append((tweetid,label))
    return annotated


def main():
    args = parse()
    #Initialize variables:


    #Sample of iterations:
    max_iteration = 1300
    total_iterations = [ 0, 15, 30, 50, 100, 150, 300, 450, 600, 750, 900, 1000, 1100, 1300]

    #Reranking:
    reranking = args.topX > 0
    params = { "topX": args.topX }
    if args.K:
        params['K'] = args.K

    #Stopwords
    if args.st:
      stopwords = readStopwords(args.st)
    else:
      stopwords = []

    #Classifier to be used:
    if args.c:
      classifier_module = eval(args.c)
    else:
      classifier_module = SklearnClassifier(SVC(kernel="linear",probability=True,class_weight='auto'))


    sampling_method = args.sm
    print args.sm

    #Tweet content files:
    id2tweet_test = readInTextFile(args.S)
    id2tweet_training = readInTextFile(args.s)

    #Features:
    if (args.t and args.T):
        trainfeatures = readFeatures(args.t)
        testfeatures = readFeatures(args.T)
    else:
        print("BoW+presence")
        trainfeatures = preprocess_tweets(id2tweet_training,stopwords)
        testfeatures = preprocess_tweets(id2tweet_test,stopwords)

    #Entity:
    current_entity = id2tweet_test[long(id2tweet_test.keys()[0])]["entity"] #all tweets belong to the same entity

    #Goldstandard:
    if args.g:
       goldstandard_training = readGoldstandard(args.g, current_entity)
    if args.G:
       goldstandard = readGoldstandard(args.G, current_entity)

    #filter out those tweets that are not in the goldstandard
    trainfeatures =  { k: trainfeatures[k] for k in goldstandard_training.keys() if k in trainfeatures.keys() }
    testfeatures = { k: testfeatures[k] for k in goldstandard.keys() if k in testfeatures.keys() }

    #Update label in trainfeatures:
    for tweetid,label in goldstandard_training.iteritems():
       if long(tweetid) in trainfeatures.keys():
         (f,l) = trainfeatures[long(tweetid)]
         trainfeatures[long(tweetid)] = (f,label)

    appended_training = {}
    appended_training.update(trainfeatures)

    sampled_ids = []
    no_sample_testing = {}
    no_sample_testing.update(testfeatures)
    related = 0

    #Compute proportion of related tweets in the training set:
    if len(appended_training.values())>0:
        related = float(len([ v for (k,v) in appended_training.values() if v =="RELATED"]))/len(appended_training.values())
    print "entity: %s related_ratio: %f"%(current_entity,related)

    if not len(testfeatures.keys()):
            print "exit"
            sys.exit()
    #Trivial cases: all tweets in the training set belongs to the same class. If so, classify all the tweets in the test to the corresponding class.
    #If proportion of related tweets is 1, classify all as 'related'.
    if related==1.0:
        if not args.o:
            for k in sampled_ids:
                print k, "RELATED"
            for k,t in no_sample_testing.iteritems():
                print k, "RELATED"
        else:
          for i in range(max_iteration+1):
             if i in total_iterations:
                    filename = "%s_%d"%(args.o,i)

                    f = file(filename, 'w')
                    f.write("entity_id\ttweet_id\tfiltering\n")

                    filename = "%s_%d"%(args.O,i)
                    fsample = file(filename, 'w')
                    for k in sampled_ids:
                      f.write("%s\t%s\t%s\n"%(current_entity, k, "RELATED"))
                      fsample.write("%s\t%s\n"%(current_entity,k))

                    for k,t in no_sample_testing.iteritems():
                            f.write("%s\t%s\t%s\n"%(current_entity, k, "RELATED"))
    #If proportion of related tweets is 0, classify all as 'unrelated'.
    elif related==0.0 and len(appended_training.values())>0:
        if not args.o:
            for k in sampled_ids:
                print k, "UNRELATED"
            for k,t in no_sample_testing.iteritems():
                print k, "UNRELATED"
        else:
            for i in range(max_iteration+1):
                if i in total_iterations:
                    filename = "%s_%d"%(args.o,i)

                    f = file(filename, 'w')
                    f.write("entity_id\ttweet_id\tfiltering\n")

                    filename = "%s_%d"%(args.O,i)
                    fsample = file(filename, 'w')
                    for k in sampled_ids:
                      f.write("%s\t%s\t%s\n"%(current_entity, k, "UNRELATED"))
                      fsample.write("%s\t%s\n"%(current_entity,k))

                    for k,t in no_sample_testing.iteritems():
                            f.write("%s\t%s\t%s\n"%(current_entity, k, "UNRELATED"))
    #Learning case:
    else:
        print "Training classifier"
        classifier = classifier_module.train(appended_training.values())

    #Initialize density
    if sampling_method == "margin_density":
            combined = {}
            for k, v in appended_training.iteritems():
                    combined[k] = v
            for k,v in no_sample_testing.iteritems():
                    combined[k] = v
            simatrix, id2row = similarityMatrix(combined)
            params['simmatrix'] = simatrix
            params['id2row'] = id2row

    #Iterate over the simulated AL loops:
    for i in range(max_iteration+1):
            print "iteration: %i"% i

            #Return list of tuples (score, tweetid)
            samples_ids = mostDiscriminateSample(classifier,
                    no_sample_testing,
                    sampling_method,
                    reranking,
                    params)
            # add the sample from the training set
            actual_noannotations = min(len(samples_ids), args.I)
            newsamples_ids = simulatedActiveAnnotation(samples_ids, id2tweet_test, goldstandard, actual_noannotations)

            if args.w <1:
                    current_weight = int((args.w * len(trainfeatures))+0.5)
            else:
                    current_weight = int(args.w)
            for w in range(current_weight):
                    newsamples = {k : (testfeatures[long(k)][0],v) for (k,v) in newsamples_ids}
            print current_weight, args.w
            appended_training.update(newsamples)
            samples = {k : (testfeatures[long(k)],goldstandard[long(k)]) for (s,k) in samples_ids}

            # remove the sample from the "to sample set"
            for s in samples_ids[:actual_noannotations]:
                    del no_sample_testing[long(s[1])]
                    sampled_ids.append(s[1])
            #Update the proportion of related tweets in the new training set:
            related = float(len([ v for (k,v) in appended_training.values() if v =="RELATED"]))/len(appended_training.values())
            print "entity: %s related_ratio: %f"%(current_entity,related)

            #Update the model
            if related <1.0 and related>0.0:
                    classifier = classifier_module.train(appended_training.values())
            #Report the results
            if i in total_iterations:
                    if related == 1.0:
                            if not args.o:
                                    for k in sampled_ids:
                                            print k, appended_training[long(k)][1]
                                    for k,t in no_sample_testing.iteritems():
                                            print k, "RELATED"
                            else:
                                    filename = "%s_%d"%(args.o,i)
                                    f = file(filename.o, 'w')
                                    f.write("entity_id\ttweet_id\tfiltering\n")

                                    filename = "%s_%d"%(args.O,i)
                                    fsample = file(filename, 'w')
                                    for k in sampled_ids:
                                            f.write("%s\t%s\t%s\n"\
                                                    %(current_entity,k,appended_training[k][1]))
                                            fsample.write("%s\t%s\n"%(current_entity,k))

                                    for k,t in no_sample_testing.iteritems():
                                            f.write("%s\t%s\t%s\n"%(current_entity,k, "RELATED"))
                    elif related == 0.0:
                            if not args.o:

                                    for k in sampled_ids:
                                            print k, appended_training[long(k)][1]
                                    for k,t in no_sample_testing.iteritems():
                                            print k, "UNRELATED"
                            else:
                                    filename = "%s_%d"%(args.o,i)
                                    f = file(filename, 'w')
                                    f.write("entity_id\ttweet_id\tfiltering\n")

                                    filename = "%s_%d"%(args.O,i)
                                    fsample = file(filename, 'w')

                                    for k in sampled_ids:
                                            f.write("%s\t%s\t%s\n"\
                                                    %(current_entity,k,appended_training[k][1]))
                                            fsample.write("%s\t%s\n"%(current_entity,k))
                                    for k,t in no_sample_testing.iteritems():
                                            f.write("%s\t%s\t%s\n"%(current_entity,k, "UNRELATED"))
                    else:
                            if not args.o:
                                    for k in sampled_ids:
                                            print k, appended_training[long(k)][1]
                                    for k,t in no_sample_testing.iteritems():
                                            print k, classifier.classify(t[0])
                            else:
                                    filename = "%s_%d"%(args.o,i)
                                    f = file(filename, 'w')
                                    f.write("entity_id\ttweet_id\tfiltering\n")
                                    filename = "%s_%d"%(args.O,i)
                                    fsample = file(filename, 'w')
                                    for k in sampled_ids:
                                            f.write("%s\t%s\t%s\n"\
                                                    %(current_entity,k,appended_training[k][1]))
                                            fsample.write("%s\t%s\n"%(current_entity,k))
                                    for k,t in no_sample_testing.iteritems():
                                            f.write("%s\t%s\t%s\n"%(current_entity,k, classifier.classify(t[0])))

if __name__ == '__main__':
    main()
