from sqlalchemy.orm import eagerload
from sqlalchemy.sql import and_

replace = {"attributes": "_Item__attributes",
           "modules": "_Fit__modules",
           "projectedModules": "_Fit__projectedModules",
           "boosters": "_Fit__boosters",
           "drones": "_Fit__drones",
           "projectedDrones": "_Fit__projectedDrones",
           "implants": "_Fit__implants",
           "character": "_Fit__character",
           "damagePattern": "_Fit__damagePattern",
           "projectedFits": "_Fit__projectedFits"}

def processEager(eager):
    if eager == None:
        return tuple()
    else:
        l = []
        if isinstance(eager, basestring):
            eager = (eager,)

        for e in eager:
            l.append(eagerload(_replacements(e)))

        return l

def _replacements(eagerString):
    splitEager = eagerString.split(".")
    for i in xrange(len(splitEager)):
        part = splitEager[i]
        replacement = replace.get(part)
        if replacement:
            splitEager[i] = replacement

    return ".".join(splitEager)

def processWhere(clause, where):
    if where is not None:
        if not hasattr(where, "__iter__"):
            where = (where,)

        for extraClause in where:
            clause = and_(clause, extraClause)

    return clause
