
def play(ICode, UserID = None, Code=None):
    if Code == ICode:
        return (UserID, ICode, len(ICode), 0)
    for i in range(0, len(Code)):
        done = False
        if Code[i] == ICode[i]:
            Code[i] = None
            done = True
        elif Code[i].lower() == ICode[i]:
            Code[i] = None
        if ICode[i] in Code and not done:
            Code[Code.index(ICode[i])] = ICode[i].upper()
    print(ICode,Code)
    return (UserID, ICode, Code.count(None), len([i for i in list(filter(None, Code)) if i.isupper()]))
while True:
    ip = input(":>").split(",")
    print(play(ICode=ip[0].split("|"),Code=ip[1].split("|")))
