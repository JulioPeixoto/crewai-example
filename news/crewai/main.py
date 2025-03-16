from crew import NewsCrew
import logging

logger = logging.getLogger(__name__)

def main():
    news_crew = NewsCrew()
    result = news_crew.run()
    logger.info("Resultado da execução da crew:")
    logger.info(result)

if __name__ == "__main__":
    main()
