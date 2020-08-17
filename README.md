
# Installing

Install directly from Git:

pip install "git+https://github.com/MaJaHa95/ml-service-wrapper.git#egg=mlservicewrapper&subdirectory=src/mlservicewrapper"

# Implementing an ML service

Write a class that matches the interface defined by `Service`:

```python
import mlservicewrapper
import mlservicewrapper.services

class SampleService(mlservicewrapper.services.Service):
    async def load(self, ctx: mlservicewrapper.contexts.ServiceContext):
        pass

    async def process(self, ctx: mlservicewrapper.contexts.ProcessContext):
        pass
```

Implement the `load` function to load models into memory and do necessary pre-work. It makes sense to parse and store service context parameters in this function, as they won't be accessible later.

The `process` function will be called many times for each `load`, and is where data should actually be handled.

## Configuration files

Each service is accompanied by a simple JSON configuration file, that tells the wrapper some basic details about the service.

* `modulePath`
  * The path, _relative to the configuration file,_ where the `Service` inheritor is defined.
* `className`
  * The name of the `Service` inheritor itself. Note that this class must be initializable with no parameters; those should be saved for the `load` function.
* `serviceInstanceName`
  * In cases when you choose to instantiate the `Service` yourself, the name of the instance exposed by the module.
* `parameters`
  * An optional dictionary of configuration-specific key-value pairs, which should be passed via the `ServiceContext` parameters. This is useful when multiple configuration files can be used for the same `Service`.
* `meta`
  * Application-level metadata, not passed to the `Service`. Useful for managing configurations internally.

## Contexts

### `ServiceContext`

A `ServiceContext` object will be passed to the `load` function when the service is first initialized. It exposes a single function, `get_parameter_value(name: str, default: str = None)`, which can be used to get a parameter from the environment. These parameters may be sourced from:
* The configuration file (using the `parameters` property), 
* Environment variables
* Other, environment-specific key-value stores

Note that all values returned by `get_parameter_value` are either `str` or `None`. It is the implementation's responsibility to sensibly parse string input and handle missing values, potentially with use of the `default` parameter. Numbers will not be parsed.

### `ProcessContext`

A `ProcessContext` object is passed to the `process` function, and exposes key details about a particular execution. It has more functions than a `ServiceContext`:

* `get_input_dataframe(name: str, required: bool = True)`
  * Returns a Pandas `DataFrame` object containing the named input dataset.
  * Note that an optional parameter `required` may be set to `False` in rare cases when an input dataset is optional.
* `set_output_dataframe(self, name: str, df: pd.DataFrame)`
  * Set the named output dataset using an existing Pandas `DataFrame`
* `get_parameter_value(name: str, required: bool = True, default: str = None) -> str`
  * Returns execution-specific parameters, **not including** those defined in the `ServiceContext`. To use service-level parameters, store them on the service instance.
  * _Heads up:_ most implementations will not use execution parameters. Consider using `ServiceContext` parameters instead. It's also advisable to provide sensible default values, either in-code or through `ServiceContext` parameters.

Depending on the deployment environment, input and output datasets may be sourced from:
* Local CSV files,
* SQL tables or queries,
* JSON documents or request bodies,
* Or other sources...

## Errors

Validating input and raising appropriate errors helps callers understand usage of the ML service. Some built-in errors may have special behaviors in supporting environments. Use the one that most specifically describes the problem.

As best practice, work to validate input datasets and parameters as early as possible. For example, test that all required categorical fields are present _before_ performing work to preprocess text ones.

### Parameter Validation

* `MissingParameterError(name: str, message: str = None)`
  * Used internally when a parameter is requested via the `get_parameter_value` function, but cannot be found on the request. Similarly to the `MissingDatasetError`, logic is likely best left to the `required` parameter on that function.
* `BadParameterError(name: str, message: str = None)`
  * Raise for all other parameter validation errors, e.g. when a string is not parsable.

### Dataset Validation

* `MissingDatasetFieldError(dataset_name: str, field_name: str, message: str = None)`
  * Used when a required field is missing from an input dataset. For example:

    ```python
    data = await ctx.get_input_dataframe("Input")

    if not "TextField" in data.columns:
        raise jnjservicewrapper.errors.MissingDatasetFieldError("Input", "TextField")
    ```
* `DatasetFieldError(dataset_name: str, field_name: str, message: str = None)`
  * Used when a dataset field _is_ present, but is otherwise invalid. Use is implementation-specific, but could describe an unparsable number field, a duplicate value in an expected-unique field, or other like input inconsistencies.
* `MissingDatasetError(dataset_name: str, message: str = None)`
  * Thrown internally when a call to `get_input_dataframe` is made when no dataset exists by the name. It is unlikely implementations will benefit from calling this error directly, and should defer to the `ProcessContext` using the `required` parameter on `get_input_dataframe`.
* `BadDatasetError(dataset_name: str, message: str = None)`
  * Base class for other errors, callable when a dataset does not match the agreed-upon contract.


# Debugging a service

Examples below use the sample service, and consequently require cloning of this repository to run.

## Write your own debug script

See `./sample_service/src/debug.py` for an example.

## Test end-to-end using configuration file

Call the debug module directly:

```bash
python -m mlservicewrapper.debug \
    --config "./sample_service/src/config.json" \
    --input-dir "./sample_service/data/input" \
    --load-params ModBy=3
```
