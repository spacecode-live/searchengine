//
//  booleanRetrieval.h
//  hits
//
//  Created by 朱 秋晗 on 15/11/22.
//  Copyright (c) 2015年 朱 秋晗. All rights reserved.
//

#ifndef hits_booleanRetrieval_h
#define hits_booleanRetrieval_h

#include <set>
#include <string>
#include <vector>
#include <sstream>
#include <cctype>
#include <algorithm>

using namespace std;

vector<int> booleanRetrieval(string query, unordered_map<string, vector<int>* > invIndex){
    transform(query.begin(), query.end(), query.begin(), ::tolower);
    vector<int> matchedPageids;
    stringstream ss(query);
    string term;
    vector<set<int>* > pageIdList;
    while (ss >> term) {
        if (!invIndex.count(term)) {
            return matchedPageids;
        }
        set<int> *pageIdsetPtr = new set<int>;
        vector<int> *pageIdsOfTerm = invIndex[term];
        for (int i = 0; i < pageIdsOfTerm->size(); i++) {
            pageIdsetPtr->insert(pageIdsOfTerm->at(i));
        }
        pageIdList.push_back(pageIdsetPtr);
    }
    for (set<int>::iterator it = pageIdList[0]->begin(); it != pageIdList[0]->end(); it++) {
        bool match = 1;
        if (pageIdList.size() > 1) {
            for (int i = 1; i < pageIdList.size(); i++) {
                if (!pageIdList[i]->count(*it)) {
                    match = 0;
                    break;
                }
            }
        }
        if (match) {
            matchedPageids.push_back(*it);
        }
    }
    return matchedPageids;
}

#endif
