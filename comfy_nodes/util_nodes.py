from easy_nodes import (
    NumberInput,
    ComfyNode,
    MaskTensor,
    StringInput,
    ImageTensor,
    Choice,
    AnyType
)
import easy_nodes


@ComfyNode()
def switch_inputs_router(
    input_a: AnyType = None,
    input_b: AnyType = None,
    input_c: AnyType = None,
    input_d: AnyType = None,
    switch: str = Choice(["a", "b", "c", "d"]),
) -> AnyType:
    """
    Switch between 3 arbitary inputs
    """
    FALLBACK = "<switch_inputs>: ERROR: Invalid switch value"

    if switch == "a":
        return input_a
    elif switch == "b":
        return input_b
    elif switch == "c":
        return input_c
    elif switch == "d":
        return input_d
    else:
        return FALLBACK
