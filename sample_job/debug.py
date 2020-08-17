import argparse
import os

import mljobwrapper
import mljobwrapper.local
import predict_job

if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description='Run predictions on sample data.')
    parser.add_argument('--level', type=int,
                        help='the level to predict', choices=[1, 2, 3], default=1)

    args = parser.parse_args()
    
    if args.level == 3:
        job_type = predict_job.InferenceLevel3
    elif args.level == 2:
        job_type = predict_job.InferenceLevel2
    else:
        job_type = predict_job.InferenceLevel1

    print("Using " + job_type.__name__)

    with job_type() as job:

        root_dir = os.path.join(os.path.dirname(__file__), '..')

        input_data_dir = os.path.join(root_dir, 'sample_data')
        output_data_dir = os.path.join(root_dir, 'test_output')

        input_name = "input"

        load_parameters = {
            "MaxSequenceLength": "100",
            "InputName": input_name,
            "ModelsDirectory": os.path.join(root_dir, "models", "level{}".format(args.level))
        }

        results = mljobwrapper.local.run(job, input_data_dir, load_parameters=load_parameters, output_file_directory=output_data_dir)

        predictions = results["Results"]
