import pytest
import TPC
import argparse
import requests
import sys
import os
import pandas as pd
import numpy as np

@pytest.fixture(scope='module')
def actual_data_response():
    return requests.get(TPC.API_URL)

def test_API_response_status_code(actual_data_response):
    '''
    Test if API returns OK response with status code 200
    '''
    assert actual_data_response.status_code == 200

def test_API_response_data_schema(actual_data_response):
    '''
    Test if response returned by API keeps certain schema
    '''
    json_response = actual_data_response.json()
    assert 'nhits' in json_response.keys()
    assert 'records' in json_response.keys()
    assert 'fields' in json_response['records'][0].keys()

@pytest.fixture()
def simple_parser_arg():
    parser = argparse.ArgumentParser()
    arg = parser.add_argument('-i')
    return arg

@pytest.mark.parametrize('filename, extensions', [
    ('test.pickle', ['.json', '.csv']),
    ('examples/test.pickle', ['.p*',]),
    ('test.xls', ['.xlsx', '.csv']),
    ])
def test_file_extension_check(simple_parser_arg, filename, extensions):
    '''
    Test if wrong extensionfile raises ArgumentError
    '''
    with pytest.raises(argparse.ArgumentError):
        TPC.check_arg_file_extension(filename, extensions, simple_parser_arg)

def test_ArgparseFactory_split():
    '''
    Test if multiple spaces in argument string are parsed right
    '''
    APF = TPC.ArgparseFactory()
    APF.add_argument("-i tests/titanic-passengers.csv    -o   tests/test_output.txt")
    assert APF.arguments == ['-i', 'tests/titanic-passengers.csv', '-o', 'tests/test_output.txt']

def test_discrepencies_csv():
    '''
    Test if changes below are included in json_result

    Changes in expected data:
        Passenger 90:
            Survived: No -> Yes
            Pclass: 3 -> 5
        Passenger 727:
            Age: 30.0 -> Young
        Passenger 797:
            Fare: 25.9292 -> 25.93 # np.isclose(25.9292, 25.93) outputs False
        Passenger 555:
            Fare: 7.775 -> 7.785
        Passenger 500:
            Deleted in expected
        Passenger 41:
            Row duplicated
        Passenger 892:
            Row added to expected (is missing in actual)
    '''
    APF = TPC.ArgparseFactory()
    APF.add_argument('-i tests/titanic-passengers.csv -o tests/test_output.txt -f')
    args = APF.parse_args()
    json_result = TPC.titanic_datasets_comparison(args, test_flag=True)
    return json_result

    assert len(json_result.keys()) == 6
    assert 90 in json_result.keys()
    assert 727 in json_result.keys()
    assert 797 in json_result.keys()
    assert 41 in json_result.keys()
    assert 555 in json_result.keys()
    assert len(json_result[90]['errors']) == 2
    
    # Wrong value
    assert json_result[727]['errors'][0]['actual_value'] == 30.0

    # Deleted row
    assert json_result[500]['errors'][0]['error_code'] == 5

    # Duplicated id
    assert json_result[41]['errors'][0]['error_code'] == 3

def test_same_discrepencies_different_file_extension():
    '''
    Test if same data from json and csv produces the same result
    '''
    input_files = ["tests/titanic-passengers.csv", "tests/titanic-passengers.json"]
    results = []
    for file in input_files:
        APF = TPC.ArgparseFactory()
        APF.add_argument(f'-i {file} -o tests/test_output.txt -f -p 90,727,797,555,500,41,892,1,2,3')
        args = APF.parse_args()
        results.append(TPC.titanic_datasets_comparison(args, test_flag=True))
    assert not len(list(set(results[0].keys()) - set(results[1].keys())))

def test_compare_series_close_floats():
    '''
    Test if numpy.isclose comparison returns proper results
    '''
    series_1 = pd.Series([0.8000000001, 14.0, 14.0, 600.00000000004])
    series_2 = pd.Series([0.8, 14.0, 14.1, 600.0])
    bool_mask = TPC.discrepencies_series_mask(series_1, series_2, isclose_flag=True)
    assert bool_mask.iloc[0] == False
    assert bool_mask.iloc[1] == False
    assert bool_mask.iloc[2] == True
    assert bool_mask.iloc[3] == False

def test_compare_series_string_among_floats():
    '''
    Test if change of series dtype is not causing problems
    '''
    series_1 = pd.Series([0.8, "string", 14.0, 600.0])
    series_2 = pd.Series([0.8, 14.0, 14.00000005, 600])
    bool_mask = TPC.discrepencies_series_mask(series_1, series_2, isclose_flag=False)
    assert bool_mask.iloc[0] == False
    assert bool_mask.iloc[1] == True
    assert bool_mask.iloc[2] == True
    assert bool_mask.iloc[3] == False

def test_compare_series_strings():
    '''
    Test if two series of dtype 'object' are compared without isclose_flag
    '''
    series_1 = pd.Series(["string1", "string2", "string3", 500.0, "14.0", "15.0"])
    series_2 = pd.Series(["string3", "string2", "string1", "500", 14.0, 15])
    bool_mask = TPC.discrepencies_series_mask(series_1, series_2, isclose_flag=False)
    assert bool_mask.iloc[0] == True
    assert bool_mask.iloc[1] == False
    assert bool_mask.iloc[2] == True
    assert bool_mask.iloc[3] == True
    assert bool_mask.iloc[4] == False
    assert bool_mask.iloc[5] == True # Not sure if "15.0" and 15 are not equal

def test_compare_series_int_float():
    '''
    Test if comparison betweend ints and floats always returns True in mask
    '''
    series_1 = pd.Series([15.0, 14.0, 13.0, 12.0])
    series_2 = pd.Series([15, 14, 13, 12])
    bool_mask = TPC.discrepencies_series_mask(series_1, series_2, isclose_flag=True)
    assert bool_mask.iloc[0] == True
    assert bool_mask.iloc[1] == True
    assert bool_mask.iloc[2] == True
    assert bool_mask.iloc[3] == True

def test_compare_series_nan_values():
    '''
    Test if NaN values are compared as equal 
    '''
    series_1 = pd.Series([15.0, 7000.0, np.nan, 5.00000005])
    series_2 = pd.Series([15.0000005, 7000.0, np.nan, np.nan])
    bool_mask = TPC.discrepencies_series_mask(series_1, series_2, isclose_flag=True)
    assert bool_mask.iloc[0] == False
    assert bool_mask.iloc[1] == False
    assert bool_mask.iloc[2] == False
    assert bool_mask.iloc[3] == True
