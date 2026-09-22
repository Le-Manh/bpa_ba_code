import tensorflow as tf

def build_model_feat(
    F: int=624,
    n_classes: int =5,
    hidden_units: tuple=(128, 64),
    norm: str="layernorm",          # "none" oder "layernorm"
    dropout: float =0.0,
    wd: float=1e-4,
    initializer: str="he_normal",
    lr: float=3e-4,
    leaky_alpha: float=0.1
):
    """
    builds the parametrized mlp model to perform a gridsearch through the parameters

    Parameters
    ----------
    F : int, default=624
        Number of Feature Dimension which will act as inputs for the Neural Network
    n_classes : int, default=5
        Number of classes which should be be returned by the network. In this case it is five but should be six to add a rest class to the finger movement
    hidden_units : tuple of int, default=(128,64)
        len(hidden_units) is the number of hidden layers and the int in the tuple is the count of units in the layer
    norm : str, default=layernorm
        Adds tf.keras.layers.LayerNormalization after the input if the value is 'layernorm' otherwise ignores it
        To differentiate between used and not used it is noted as none or layernorm
    dropout : float, default=0.0
        Adds a dropout between the hidden layers and before the the output layer, if the value is different then 0
    wd : float, default=1e-4
        Value to give to the regularizer l2 it's factor
    initializer : str, default='he_normal'
        Value to initialize the weights. Supports the str identifiers of keras.initializers
    lr: float, default=3e-4
        Value of the Learning Rate to give Adam
    leaky_alpha: float, default=0.1
        value to give LeakyReLU as negative_slope which replaces the parameter which was used before alpha

    Returns
    -------
    keras.Model
        the compiled model with the given arguments
    """
    init = tf.keras.initializers.get(initializer)

    x_in = tf.keras.layers.Input(shape=(F,), name="feat")
    x = x_in
    if norm == "layernorm":
        x = tf.keras.layers.LayerNormalization()(x)

    for units in hidden_units:
        x = tf.keras.layers.Dense(
            units,
            activation=None,
            kernel_initializer=init,
            kernel_regularizer=tf.keras.regularizers.l2(wd) if wd and wd > 0 else None,
        )(x)
        x = tf.keras.layers.LeakyReLU(negative_slope=leaky_alpha)(x)
        if dropout and dropout > 0:
            x = tf.keras.layers.Dropout(dropout)(x)

    out = tf.keras.layers.Dense(n_classes, activation="softmax")(x)

    model = tf.keras.Model(inputs=x_in, outputs=out)
    model.compile(
        optimizer=tf.keras.optimizers.Adam(learning_rate=lr),
        loss=tf.keras.losses.SparseCategoricalCrossentropy(),
        metrics=[
            "accuracy",
            tf.keras.metrics.SparseCategoricalCrossentropy(name="ce"),
        ],
    )
    return model
