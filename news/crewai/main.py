from crew import NewsCrew

def main():
    news_crew = NewsCrew()
    result = news_crew.run()
    print("Resultado da execução da crew:")
    print(result)

if __name__ == "__main__":
    main()
