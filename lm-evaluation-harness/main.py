import argparse
import json
import logging
import os

from lm_eval import tasks, evaluator, utils

logging.getLogger("openai").setLevel(logging.WARNING)


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("--model", required=True)
    parser.add_argument("--model_args", default="")
    parser.add_argument("--tasks", default=None, choices=utils.MultiChoice(tasks.ALL_TASKS))
    parser.add_argument("--provide_description", action="store_true")
    parser.add_argument("--num_fewshot", type=int, default=0)
    parser.add_argument("--batch_size", type=str, default=None)
    parser.add_argument("--max_batch_size", type=int, default=None,
                        help="Maximal batch size to try with --batch_size auto")
    parser.add_argument("--device", type=str, default=None)
    parser.add_argument("--output_path", default=None)
    parser.add_argument("--limit", type=float, default=None,
                        help="Limit the number of examples per task. "
                             "If <1, limit is a percentage of the total number of examples.")
    parser.add_argument("--data_sampling", type=float, default=None)
    parser.add_argument("--no_cache", action="store_true")
    parser.add_argument("--decontamination_ngrams_path", default=None)
    parser.add_argument("--description_dict_path", default=None)
    parser.add_argument("--check_integrity", action="store_true")
    parser.add_argument("--write_out", action="store_true", default=False)
    parser.add_argument("--output_base_path", type=str, default=None)

    parser.add_argument("--output_template", type=str, default=None)
    parser.add_argument("--rep_topics", action="store_true")
    parser.add_argument("--topic_keywords", action="store_true")
    parser.add_argument("--use_stops", action="store_true")
    parser.add_argument("--parallel_topics", action="store_true")
    parser.add_argument("--seed", type=int, default=1234)
    parser.add_argument("--bootstrap_iters", type=int, default=1000)
    parser.add_argument("--trim_excess", action="store_true")
    parser.add_argument("--domain_label", action="store_true")
    parser.add_argument("--randoms", action="store_true")
    parser.add_argument("--verbose", action="store_true")
    parser.add_argument("--domain_random", action="store_true")
    parser.add_argument("--true_random", action="store_true")
    parser.add_argument("--all_langs", action="store_true")
    parser.add_argument("--bm25", action="store_true")
    parser.add_argument("--sent_sim", action="store_true")
    parser.add_argument("--seen", action="store_true")
    parser.add_argument("--top_n", action="store_true")

    parser.add_argument("--topic_model", type=str, default=None)




    return parser.parse_args()


def main():
    args = parse_args()

    assert not args.provide_description  # not implemented

    if args.limit:
        print(
            "WARNING: --limit SHOULD ONLY BE USED FOR TESTING. REAL METRICS SHOULD NOT BE COMPUTED USING LIMIT."
        )

    if args.tasks is None:
        task_names = tasks.ALL_TASKS
    else:
        task_names = utils.pattern_match(args.tasks.split(","), tasks.ALL_TASKS)
    
    tasks.topic_model = args.topic_model

    print(f"Selected Tasks: {task_names}")

    description_dict = {}
    if args.description_dict_path:
        with open(args.description_dict_path, "r") as f:
            description_dict = json.load(f)

    results = evaluator.simple_evaluate(
        model=args.model,
        model_args=args.model_args,
        tasks=task_names,
        num_fewshot=args.num_fewshot,
        batch_size=args.batch_size,
        max_batch_size=args.max_batch_size,
        device=args.device,
        no_cache=args.no_cache,
        limit=args.limit,
        description_dict=description_dict,
        decontamination_ngrams_path=args.decontamination_ngrams_path,
        check_integrity=args.check_integrity,
        write_out=args.write_out,
        output_base_path=args.output_base_path,
        output_template=args.output_template,
        rep_topics=args.rep_topics,
        topic_keywords=args.topic_keywords,
        use_stops=args.use_stops,
        parallel_topics=args.parallel_topics,
        seed=args.seed,
        bootstrap_iters=args.bootstrap_iters,
        trim_excess=args.trim_excess,
        topic_model=args.topic_model,
        domain_label=args.domain_label,
        randoms=args.randoms,
        verbose=args.verbose,
        domain_random=args.domain_random,
        true_random=args.true_random,
        all_langs=args.all_langs,
        bm25=args.bm25,
        sent_sim=args.sent_sim,
        seen=args.seen,
        top_n=args.top_n
    )

    dumped = json.dumps(results, indent=2)
    print(dumped)

    if args.output_path:
        os.makedirs(os.path.dirname(args.output_path), exist_ok=True)
        with open(args.output_path, "w") as f:
            f.write(dumped)

    batch_sizes = ",".join(map(str, results["config"]["batch_sizes"]))
    print(
        f"{args.model} ({args.model_args}), limit: {args.limit}, provide_description: {args.provide_description}, "
        f"num_fewshot: {args.num_fewshot}, batch_size: {args.batch_size}{f' ({batch_sizes})' if batch_sizes else ''}"
    )
    print(evaluator.make_table(results))


if __name__ == "__main__":
    main()
