#include <getopt.h>
#include <iostream>
#include <string>
#include "readFiles.h"
#include "booleanRetrieval.h"
#include <map>
#include <cmath>
#include "deepCopyHits.h"

// using namespace std;

int main(int argc, char *argv[])
{
    if (argc != 8) {
        cerr<<"You should input exactly 7 arguments!"<<endl;
        exit(1);
    }
    string hstr = argv[1];
    string mode = argv[2];
    string valuestr = argv[3];
    string query = argv[4];
    string inputNetFile = argv[5];
    string inputInvindexFile = argv[6];
    string outputFile = argv[7];

	unordered_map<string, vector<int>* > invIndex;
    unordered_map<int, string> netNodes;
    unordered_map<int, vector<int>* > netPointing;
    unordered_map<int, vector<int>* > netPointed;
	
	readNet(inputNetFile, netNodes, netPointing, netPointed);
    readInvindex(inputInvindexFile, invIndex);

    vector<int> matchedPageids = booleanRetrieval(query, invIndex);
    if (matchedPageids.size() == 0) {
        cout<<"No matched pages!"<<endl;
        exit(1);
    }
    int h = atoi(hstr.c_str());
    if (matchedPageids.size() < h) {
        h = int(matchedPageids.size());
    }
    set<int> seedSet(matchedPageids.begin(), matchedPageids.begin()+h);
    set<int> baseSet(seedSet);
    for (set<int>::iterator it = seedSet.begin(); it != seedSet.end(); it++) {
        set<int> relatedNodes;
        if (netPointing.count(*it)) {
            relatedNodes.insert(netPointing[*it]->begin(), netPointing[*it]->end());
        }
        if (netPointed.count(*it)) {
            relatedNodes.insert(netPointed[*it]->begin(), netPointed[*it]->end());
        }
        set<int>::iterator related_it = relatedNodes.begin();
        int counter = 0;
        while (related_it != relatedNodes.end() && counter < 50) {
            if (!seedSet.count(*related_it)) {
                baseSet.insert(*related_it);
                counter++;
            }
            related_it++;
        }
    }
    
    map<int, page* > hits;
    for (set<int>::iterator it = baseSet.begin(); it != baseSet.end(); it++) {
        page *pagePtr = new page;
        pagePtr->auth = 1;
        pagePtr->hub = 1;
        hits[*it] = pagePtr;
    }
    
    map<int, page*> lastHits;
    lastHits = deepCopyHits(hits);
    
    if (mode == "-k") {
        int kvalue = atoi(valuestr.c_str());
        for (int i = 0; i < kvalue; i++) {
            double norm = 0;
            for (map<int, page*>::iterator it = hits.begin(); it != hits.end(); it++) {
                it->second->auth = 0;
                if (netPointed.count(it->first)) {
                    for (int j = 0; j < netPointed[it->first]->size(); j++) {
                        if (baseSet.count(netPointed[it->first]->at(j))) {
                            it->second->auth += lastHits[netPointed[it->first]->at(j)]->hub;
                        }
                    }
                }
                norm += pow(it->second->auth, 2);
            }
            norm = sqrt(norm);
            for (map<int, page*>::iterator it = hits.begin(); it != hits.end(); it++) {
                it->second->auth /= norm;
            }
            norm = 0;
            for (map<int, page*>::iterator it = hits.begin(); it != hits.end(); it++) {
                it->second->hub = 0;
                if (netPointing.count(it->first)) {
                    for (int j = 0; j < netPointing[it->first]->size(); j++) {
                        if (baseSet.count(netPointing[it->first]->at(j))) {
                            it->second->hub += lastHits[netPointing[it->first]->at(j)]->auth;
                        }
                    }
                }
                norm += pow(it->second->hub, 2);
            }
            norm = sqrt(norm);
            for (map<int, page*>::iterator it = hits.begin(); it != hits.end(); it++) {
                it->second->hub /= norm;
            }
            lastHits = deepCopyHits(hits);
        }
    }
    
    if (mode == "-converge") {
        double x = atof(valuestr.c_str());
        bool converge = 0;
        while (!converge) {
            cout<<"rounds"<<endl;
            converge = 1;
            double norm = 0;
            for (map<int, page*>::iterator it = hits.begin(); it != hits.end(); it++) {
                it->second->auth = 0;
                if (netPointed.count(it->first)) {
                    for (int j = 0; j < netPointed[it->first]->size(); j++) {
                        if (baseSet.count(netPointed[it->first]->at(j))) {
                            it->second->auth += lastHits[netPointed[it->first]->at(j)]->hub;
                        }
                    }
                }
                norm += pow(it->second->auth, 2);
            }
            norm = sqrt(norm);
            for (map<int, page*>::iterator it = hits.begin(); it != hits.end(); it++) {
                it->second->auth /= norm;
            }
            for (map<int, page*>::iterator it = hits.begin(); it != hits.end(); it++) {
                double change = abs(it->second->auth - lastHits[it->first]->auth) / lastHits[it->first]->auth;
                if (change > x) {
                    converge = 0;
                    break;
                }
            }
            norm = 0;
            for (map<int, page*>::iterator it = hits.begin(); it != hits.end(); it++) {
                it->second->hub = 0;
                if (netPointing.count(it->first)) {
                    for (int j = 0; j < netPointing[it->first]->size(); j++) {
                        if (baseSet.count(netPointing[it->first]->at(j))) {
                            it->second->hub += lastHits[netPointing[it->first]->at(j)]->auth;
                        }
                    }
                }
                norm += pow(it->second->hub, 2);
            }
            norm = sqrt(norm);
            for (map<int, page*>::iterator it = hits.begin(); it != hits.end(); it++) {
                it->second->hub /= norm;
            }
            for (map<int, page*>::iterator it = hits.begin(); it != hits.end(); it++) {
                double change = abs(it->second->hub - lastHits[it->first]->hub) / lastHits[it->first]->hub;
                if (change > x) {
                    converge = 0;
                    break;
                }
            }
            lastHits = deepCopyHits(hits);
        }
    }
    
    ofstream outFile;
    outFile.open(outputFile);
    for (map<int, page* >::iterator it = hits.begin(); it != hits.end(); it++) {
        outFile<<it->first<<","<<it->second->hub<<","<<it->second->auth<<"\n";
    }
    outFile.close();
    
	return 0;
}