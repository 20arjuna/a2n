def createSummaryMatrix (paragraghList):
    mat = []
    for paragragh in paragraghList:
        sentencesList = splitParagraphIntoSentences(paragraph)
        wsaList = []
        for sentence in sentencesList:
            wsaList.append(wsa(sentence))
        mat.append(wsaList)
    return mat

        
