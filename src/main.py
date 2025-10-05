from lexer.Lexer import Lexer


if __name__ == "__main__":
    with open("../tests/hello_world.minipar") as f:
        source = f.read()
    #print(source)

    lexer = Lexer(source)
    tokens = lexer.tokenize()

    for t in tokens:
        print(t)

