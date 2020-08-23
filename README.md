
[![Release](https://github.com/ml-service-wrapper/ml-service-wrapper-core/workflows/Create%20Release/badge.svg)](https://github.com/ml-service-wrapper/ml-service-wrapper-core/releases/latest)
[![PyPI Latest Release](https://img.shields.io/pypi/v/mlservicewrapper-core.svg)](https://pypi.org/project/mlservicewrapper-core/)

# Installing

* Install using pip
    ```
    pip install mlservicewrapper-core
    ```
* Install directly from [the latest GitHub Release](https://github.com/ml-service-wrapper/ml-service-wrapper-core/releases/latest).
* Install from source
    ```
    git clone https://github.com/ml-service-wrapper/ml-service-wrapper-core.git
    cd ml-service-wrapper
    pip install .
    ```

# Implementing an ML service

Write a class that matches the interface defined by `Service`:

```python
import mlservicewrapper
import mlservicewrapper.core.services

class SampleService(mlservicewrapper.core.services.Service):
    async def load(self, ctx: mlservicewrapper.core.contexts.ServiceContext):
        pass

    async def process(self, ctx: mlservicewrapper.core.contexts.ProcessContext):
        pass

    def dispose(self):
        pass
```

The three functions describe the three phases of service lifetime:

1. `load` is called when the service is first initializing, and should load models into memory and do necessary pre-work. It makes sense to parse and store [`ServiceContext`](#servicecontext) parameters in this function, as they won't be accessible later.
2. `process` will be called many times for each `load`, and is where data should actually be handled. See [`ProcessContext`](#processcontext) for how to process data.
3. `dispose` _may or may not be called,_ and is optional, but should be used for cleanup tasks during service shutdown, e.g. disposal of handles or temporary files.

## Contexts

### `ServiceContext`

A `ServiceContext` object will be passed to the `load` function when the service is first initialized. It exposes a single function:

* `get_parameter_value(name: str, required: bool = True, default: str = None)`
  * Used to get a parameter from the environment. These parameters may be sourced from:
    * A configuration file (using the `parameters` property)
    * Environment variables
    * Other, environment-specific key-value stores
  * Note that all parameter values are either type `str` or `None`. It is the implementation's responsibility to parse string input and handle missing values, potentially with use of the `default` parameter. Numbers will not be parsed.
  * Service parameters are considered required unless `required` is specified as `False`, **or** a non-`None` value is passed as a `default`.

### `ProcessContext`

A `ProcessContext` object is passed to the `process` function, and exposes key details about a particular execution. It has more functions than a `ServiceContext`:

* `get_input_dataframe(name: str, required: bool = True)`
  * Returns a Pandas `DataFrame` object containing the named input dataset.
  * Note that an optional parameter `required` may be set to `False` in rare cases when an input dataset is optional.
* `set_output_dataframe(self, name: str, df: pd.DataFrame)`
  * Set the named output dataset using an existing Pandas `DataFrame`
* `get_parameter_value(name: str, required: bool = True, default: str = None) -> str`
  * Returns execution-specific parameters, **not including** those defined in the `ServiceContext`. To use service-level parameters, store them on the service instance.
  * Process parameters are considered required unless `required` is specified as `False`, **or** a non-`None` value is passed as a `default`.
  * _Heads up:_ most implementations will not use execution parameters. Consider using `ServiceContext` parameters instead. It's also advisable to provide sensible default values, either in-code or through `ServiceContext` parameters.

Depending on the deployment environment, input and output datasets may be sourced from:
* Local CSV files,
* SQL tables or queries,
* JSON documents or request bodies, or
* Other sources...

## Validation

Validating input and raising appropriate errors helps callers understand usage of the ML service. Some built-in errors may have special behaviors in supporting environments. Use the one that most specifically describes the problem.

As best practice, work to validate input datasets and parameters as early as possible. For example, test that all required categorical fields are present _before_ performing work to preprocess text ones.

### Parameters

* `MissingParameterError(name: str, message: str = None)`
  * Used internally when a parameter is requested via the `get_parameter_value` function, but cannot be found on the request. Similarly to the `MissingDatasetError`, logic is likely best left to the `required` parameter on that function.
* `BadParameterError(name: str, message: str = None)`
  * Raise for all other parameter validation errors, e.g. when a string is not parsable.

### Datasets

* `MissingDatasetFieldError(dataset_name: str, field_name: str, message: str = None)`
  * Used when a required field is missing from an input dataset. For example:
* `DatasetFieldError(dataset_name: str, field_name: str, message: str = None)`
  * Used when a dataset field _is_ present, but is otherwise invalid. Use is implementation-specific, but could describe an unparsable number field, a duplicate value in an expected-unique field, or other like input inconsistencies.
* `MissingDatasetError(dataset_name: str, message: str = None)`
  * Thrown internally when a call to `get_input_dataframe` is made when no dataset exists by the name. It is unlikely implementations will benefit from calling this error directly, and should defer to the `ProcessContext` using the `required` parameter on `get_input_dataframe`.
* `BadDatasetError(dataset_name: str, message: str = None)`
  * Base class for other errors, callable when a dataset does not match the agreed-upon contract.

## Configuration files

Each service is accompanied by a simple JSON configuration file, that tells the wrapper some basic details about the service.

* `modulePath`
  * The path, _relative to the configuration file,_ where the `Service` inheritor is defined.
* `className`
  * The name of the `Service` inheritor itself. Note that this class must be initializable with no parameters; those should be saved for the `load` function.
* `serviceInstanceName`
  * In cases when you choose to instantiate the `Service` yourself, the name of the instance exposed by the module.
  * Only used if `className` is omitted.
* `parameters`
  * An optional dictionary of configuration-specific key-value pairs, which should be passed via the `ServiceContext` parameters. This is useful when multiple configuration files can be used for the same `Service`.
* `meta`
  * Application-level metadata, not passed to the `Service`. Useful for managing configurations internally.

Note that `modulePath` is required, along with _either_ `className` or `serviceInstanceName`.

## Naming Conventions

By nature of its configurability, external type-checking is not possible. [Validation](#validation) can help to identify errors, but only at runtime. As consequence, a consistent naming schema is important to reducing unnecessary cycles.

Follow simple rules when naming parameters and datasets:
* Use Pascal Case (e.g. `MaxValue`)
* Use only letters and numbers
* Be concise, but descriptive
* Be consistent with casing

# Debugging a service

Examples below use the sample service, and consequently require cloning of this repository to run.

## Write your own debug script

See `./sample/1_simple/src/debug.py` for an example.

## Test end-to-end using a configuration file

Call the debug module directly. The provided configuration file is parsed, just like it would be in a production environment.

```bash
python -m mlservicewrapper.core.debug \
    --config "./sample/1_simple/src/config.json" \
    --input-dir "./sample/1_simple/data/input" \
    --load-params ModBy=3
```

| Parameter | Required? | Description | Example |
| --------------- | --------------- | --------------- | --------------- |
| --config | **Yes** | Path to service configuration file | `--config "./sample/1_simple/src/config.json"` |
| --input-dir | No | Path to input directory. Input datasets will be looked up within the directory. | `--input-dir "./sample/1_simple/data/input"` |
| --input-paths | No | Path mapping for input datasets. Multiple values can be comma-delimited, and each value takes the form of `<dataset name>=<path>`. Explicitly-pathed datasets will override any files from `--input-dir`, if both are provided. | `--input-paths Data=./sample/1_simple/data/input/Data.csv` |
| --output-dir | No | Path to output directory. Output datasets will be looked up within the directory. | `--output-dir "./sample/1_simple/data/output"` |
| --output-paths | No | Path mapping for output datasets. Multiple values can be comma-delimited, and each value takes the form of `<dataset name>=<path>`. Explicitly-pathed datasets will override any files from `--output-dir`, if both are provided. | `--output-paths Data=./sample/1_simple/data/output/Data.csv` |
| --load-params | No | Values for `ServiceContext` parameters. Multiple values can be comma-delimited, and each value takes the form of `<key>=<value>` | `--load-params ModBy=3` |
| --run-params | No | Values for `ProcessContext` parameters. Multiple values can be comma-delimited, and each value takes the form of `<key>=<value>` | `--run-params RuntimeOption=OptionValue` |
| --split-dataset-for-perf | No | Runs performance analysis against the named dataset. This involves splitting the dataset into one-row chunks and calling `process` against each row independently, timing each execution, and reporting statistics. This is meant to help simulate a runtime environment where only one row is received at a time (e.g. for HTTP clients that don't use batching.) | `--split-dataset-for-perf Data` |
| --assess-accuracy | No | Calculates classification accuracy for the named input and output fields. This is useful when testing on a pre-labeled data file that contains truth labels which are ignored by the `process` call itself, for example a file used for training. Accuracy is calculated as the percentage of time the value in the input dataset field is exactly equal to that in the output dataset, meaning formatting (including case and whitespace) must be taken into consideration. | `--assess-accuracy InputData.ActualLabel=OutputData.PredictedLabel` |
| --profile-processing-to-file | No | Runs a [cProfile profiler](https://docs.python.org/3/library/profile.html) against the service `process` call, and outputs the results to the specified file path. These results can then be read with `pstats.Stats`. This can be particularly useful when paired with `--split-dataset-for-perf`, to highlight bottlenecks that occur across many executions. | `--profile-processing-to-file "./profile"` |


# Host and Deploy

Use a host to run the service in production. A host will use its own implementation for contexts, which could pull input datasets from unexpected locations.

At present, there is only one host natively supported:

* [ml-service-wrapper-host-http](https://github.com/ml-service-wrapper/ml-service-wrapper-host-http), which wraps the ML service as an HTTP endpoint, exposing it with JSON endpoints.
