//
//  deepCopyHits.h
//  hits
//
//  Created by 朱 秋晗 on 15/11/23.
//  Copyright (c) 2015年 朱 秋晗. All rights reserved.
//

#ifndef hits_deepCopyHits_h
#define hits_deepCopyHits_h

#include <map>

using namespace std;

struct page{
    double auth;
    double hub;
};

map<int, page*> deepCopyHits(map<int, page*> hits){
    map<int, page*> resultHits;
    for (map<int, page*>::iterator it = hits.begin(); it != hits.end(); it++) {
        page *pagePtr = new page;
        pagePtr->auth = it->second->auth;
        pagePtr->hub = it->second->hub;
        resultHits[it->first] = pagePtr;
    }
    return resultHits;
}

#endif
