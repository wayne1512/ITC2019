from parseInput import parse_xml
from penaltyCalc import calculate_total_penalty
from util import extract_class_list, random_gene, get_gene_maximums

if __name__ == "__main__":
    file_path = "input.xml"
    problem = parse_xml(file_path)

    classes = extract_class_list(problem)

    maximumGenes = get_gene_maximums(classes)
    print(maximumGenes)
    for _ in range(100):
        rand = random_gene(problem, maximumGenes)
        calculate_total_penalty(problem, classes, rand)
    print(rand)
